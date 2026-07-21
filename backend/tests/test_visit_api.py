from datetime import timedelta
from zoneinfo import ZoneInfo

import pytest
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.utils.dateparse import parse_datetime

from apps.accounts.models import Card, CardBinding
from apps.accounts.uid import digest_card_uid, mask_card_uid
from apps.scenes.models import Spot
from apps.visits.models import CheckinEvent, VisitSession


def make_session(user, scene):
    now = timezone.now()
    return VisitSession.objects.create(
        user=user,
        scene=scene,
        local_date=now.astimezone(ZoneInfo(scene.timezone)).date(),
        started_at=now,
        last_checkin_at=now,
    )


def make_event(*, session, device, spot, card, offset=0, status="accepted"):
    binding = CardBinding.objects.get(user=session.user, card=card)
    event = CheckinEvent.objects.create(
        event_id=f"event-{spot.slug}-{offset}-{status}",
        device=device,
        spot=spot,
        user=session.user if status == "accepted" else None,
        card=card,
        card_binding=binding,
        visit_session=session if status == "accepted" else None,
        card_uid_hmac=card.uid_hmac,
        checkin_type="rfid",
        status=status,
        failure_code="" if status == "accepted" else "CARD_DISABLED",
    )
    received_at = timezone.now() + timedelta(minutes=offset)
    CheckinEvent.objects.filter(id=event.id).update(received_at=received_at)
    event.refresh_from_db()
    return event


@pytest.mark.django_db
def test_today_visit_aggregates_cards_and_deduplicates_spots(
    auth_client,
    user,
    scene,
    spot,
    device,
    bound_cards,
):
    second_spot = Spot.objects.create(
        scene=scene,
        slug="lake",
        name="明远湖",
        category="landmark",
        map_x="0.50000",
        map_y="0.50000",
        status="published",
    )
    session = make_session(user, scene)
    make_event(session=session, device=device, spot=spot, card=bound_cards[0], offset=1)
    make_event(session=session, device=device, spot=second_spot, card=bound_cards[1], offset=2)
    make_event(session=session, device=device, spot=spot, card=bound_cards[0], offset=3)

    response = auth_client.get(f"/api/v1/me/visits/today?scene={scene.slug}")

    assert response.status_code == 200
    data = response.json()["data"]
    assert data["checked_spot_count"] == 2
    assert data["event_count"] == 3
    assert [item["spot_id"] for item in data["route"]] == [
        str(spot.id),
        str(second_spot.id),
    ]


@pytest.mark.django_db
def test_today_visit_without_events_returns_zero_progress(auth_client, scene, spot):
    response = auth_client.get(f"/api/v1/me/visits/today?scene={scene.slug}")

    assert response.status_code == 200
    assert response.json()["data"]["visit_id"] is None
    assert response.json()["data"]["checked_spot_count"] == 0
    assert response.json()["data"]["total_spot_count"] == 1


@pytest.mark.django_db
def test_card_history_supports_historical_owner_and_blocks_other_user(
    auth_client,
    user,
    scene,
    spot,
    device,
    bound_cards,
):
    session = make_session(user, scene)
    make_event(session=session, device=device, spot=spot, card=bound_cards[0])
    binding = CardBinding.objects.get(user=user, card=bound_cards[0])
    binding.unbound_at = timezone.now()
    binding.is_primary = False
    binding.save(update_fields=("unbound_at", "is_primary"))
    stranger = get_user_model().objects.create_user(username="stranger")
    stranger_card = Card.objects.create(
        serial_no="SCU-JA-STRANGER",
        uid_hmac=digest_card_uid("0499999999"),
        uid_masked=mask_card_uid("0499999999"),
    )
    CardBinding.objects.create(user=stranger, card=stranger_card, is_primary=True)

    history = auth_client.get(f"/api/v1/me/cards/{bound_cards[0].id}/checkins")
    forbidden = auth_client.get(f"/api/v1/me/cards/{stranger_card.id}/checkins")

    assert history.status_code == 200
    assert len(history.json()["data"]["items"]) == 1
    assert forbidden.status_code == 404


@pytest.mark.django_db
def test_personal_checkins_exclude_rejected_and_support_filters(
    auth_client,
    user,
    scene,
    spot,
    device,
    bound_cards,
):
    second_spot = Spot.objects.create(
        scene=scene,
        slug="lake",
        name="明远湖",
        category="landmark",
        map_x="0.50000",
        map_y="0.50000",
        status="published",
    )
    session = make_session(user, scene)
    make_event(session=session, device=device, spot=spot, card=bound_cards[0], offset=1)
    make_event(session=session, device=device, spot=second_spot, card=bound_cards[1], offset=2)
    make_event(
        session=session,
        device=device,
        spot=spot,
        card=bound_cards[0],
        offset=3,
        status="rejected",
    )

    response = auth_client.get(
        f"/api/v1/me/checkins?card_id={bound_cards[0].id}&page=1&page_size=1"
    )

    assert response.status_code == 200
    assert len(response.json()["data"]["items"]) == 1
    assert response.json()["data"]["items"][0]["spot_id"] == str(spot.id)
    assert response.json()["meta"]["total"] == 1


@pytest.mark.django_db
def test_authenticated_spot_detail_includes_personal_checkin_status(
    auth_client,
    user,
    scene,
    spot,
    device,
    bound_cards,
    client,
):
    session = make_session(user, scene)
    event = make_event(session=session, device=device, spot=spot, card=bound_cards[0])

    personal = auth_client.get(f"/api/v1/spots/{spot.id}")
    anonymous = client.get(f"/api/v1/spots/{spot.id}")

    assert personal.json()["data"]["is_checked_in"] is True
    assert parse_datetime(personal.json()["data"]["first_checked_in_at"]) == event.received_at
    assert personal.json()["data"]["distance_basis"] == "scene_map_coordinates"
    assert anonymous.json()["data"]["is_checked_in"] is False


@pytest.mark.django_db
def test_home_combines_cards_progress_latest_event_and_recommendations(
    auth_client,
    user,
    scene,
    spot,
    device,
    bound_cards,
):
    unvisited = Spot.objects.create(
        scene=scene,
        slug="lake",
        name="明远湖",
        category="landmark",
        map_x="0.50000",
        map_y="0.50000",
        status="published",
    )
    session = make_session(user, scene)
    event = make_event(session=session, device=device, spot=spot, card=bound_cards[0])

    response = auth_client.get(f"/api/v1/me/home?scene={scene.slug}")

    data = response.json()["data"]
    assert response.status_code == 200
    assert data["active_card_count"] == 2
    assert data["primary_card"]["card_id"] == str(bound_cards[0].id)
    assert data["visit"]["checked_spot_count"] == 1
    assert data["latest_checkin"]["id"] == str(event.id)
    assert [item["id"] for item in data["recommended_spots"]] == [str(unvisited.id)]
