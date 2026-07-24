from datetime import UTC, datetime
from zoneinfo import ZoneInfo

import pytest

from apps.accounts.models import Card
from apps.accounts.uid import digest_card_uid, mask_card_uid
from apps.scenes.models import Spot
from apps.visits.models import CheckinEvent, VisitSession


@pytest.mark.django_db
def test_two_cards_for_one_user_share_daily_session(
    device_client,
    device,
    user,
    bound_cards,
):
    first = device_client.post_checkin(
        device=device,
        card=bound_cards[0],
        event_id="event-a",
    )
    second = device_client.post_checkin(
        device=device,
        card=bound_cards[1],
        event_id="event-b",
    )

    assert first.status_code == second.status_code == 200
    assert VisitSession.objects.filter(user=user, scene=device.scene).count() == 1
    assert CheckinEvent.objects.filter(user=user, status="accepted").count() == 2
    assert first.json()["data"]["feedback_code"] == "EVENT_ACCEPTED"
    assert "visitor" not in str(first.json())
    assert bound_cards[0].plain_uid not in str(first.json())


@pytest.mark.django_db
def test_repeating_device_event_returns_original_result(device_client, device, bound_cards):
    first = device_client.post_checkin(
        device=device,
        card=bound_cards[0],
        event_id="same-event",
    )
    second = device_client.post_checkin(
        device=device,
        card=bound_cards[0],
        event_id="same-event",
    )

    assert second.status_code == 200
    assert second.json()["data"] == first.json()["data"]
    assert CheckinEvent.objects.filter(device=device, event_id="same-event").count() == 1


@pytest.mark.django_db
def test_unregistered_uid_creates_rejected_event_without_session(device_client, device):
    unknown_card = Card(serial_no="UNKNOWN")
    unknown_card.plain_uid = "04FFFFFFFF"

    response = device_client.post_checkin(
        device=device,
        card=unknown_card,
        event_id="unknown-card",
    )

    assert response.status_code == 200
    assert response.json()["data"]["failure_code"] == "CARD_UNREGISTERED"
    event = CheckinEvent.objects.get(device=device, event_id="unknown-card")
    assert event.status == CheckinEvent.Status.REJECTED
    assert event.visit_session is None
    assert VisitSession.objects.count() == 0


@pytest.mark.django_db
def test_unbound_and_disabled_cards_are_rejected(device_client, device, bound_cards):
    unbound = Card.objects.create(
        serial_no="SCU-JA-UNBOUND",
        uid_hmac=digest_card_uid("0411111111"),
        uid_masked=mask_card_uid("0411111111"),
    )
    unbound.plain_uid = "0411111111"
    bound_cards[0].status = Card.Status.DISABLED
    bound_cards[0].save(update_fields=("status",))

    unbound_response = device_client.post_checkin(
        device=device,
        card=unbound,
        event_id="unbound-card",
    )
    disabled_response = device_client.post_checkin(
        device=device,
        card=bound_cards[0],
        event_id="disabled-card",
    )

    assert unbound_response.json()["data"]["failure_code"] == "CARD_UNBOUND"
    assert disabled_response.json()["data"]["failure_code"] == "CARD_DISABLED"
    assert VisitSession.objects.count() == 0


@pytest.mark.django_db
def test_spot_mismatch_is_rejected_before_card_processing(
    device_client,
    device,
    bound_cards,
):
    other_spot = Spot.objects.create(
        scene=device.scene,
        slug="lake",
        name="明远湖",
        category="landmark",
        map_x="0.50000",
        map_y="0.50000",
        status="published",
    )

    response = device_client.post_checkin(
        device=device,
        card=bound_cards[0],
        event_id="wrong-spot",
        spot=other_spot,
    )

    assert response.status_code == 200
    assert response.json()["data"]["failure_code"] == "SPOT_MISMATCH"
    event = CheckinEvent.objects.get(event_id="wrong-spot")
    assert event.card is None
    assert event.visit_session is None


@pytest.mark.django_db
def test_server_scene_date_controls_sessions_not_device_time(
    monkeypatch,
    device_client,
    device,
    user,
    bound_cards,
):
    first_server_time = datetime(2026, 7, 21, 2, 0, tzinfo=UTC)
    second_server_time = datetime(2026, 7, 22, 2, 0, tzinfo=UTC)
    monkeypatch.setattr("apps.visits.services.timezone.now", lambda: first_server_time)
    first = device_client.post_checkin(
        device=device,
        card=bound_cards[0],
        event_id="day-one",
        device_time="2035-01-01T23:59:59+08:00",
    )
    monkeypatch.setattr("apps.visits.services.timezone.now", lambda: second_server_time)
    second = device_client.post_checkin(
        device=device,
        card=bound_cards[0],
        event_id="day-two",
        device_time="2020-01-01T00:00:00+08:00",
    )

    expected_dates = {
        first_server_time.astimezone(ZoneInfo(device.scene.timezone)).date(),
        second_server_time.astimezone(ZoneInfo(device.scene.timezone)).date(),
    }
    assert first.status_code == second.status_code == 200
    assert (
        set(VisitSession.objects.filter(user=user).values_list("local_date", flat=True))
        == expected_dates
    )
