from datetime import timedelta

import pytest
from django.contrib.auth import get_user_model
from django.utils import timezone

from apps.accounts.models import Card, CardBinding
from apps.iot.models import Device
from apps.scenes.models import PublishStatus, Route, Scene, Spot, SpotMedia
from apps.visits.models import CheckinEvent, VisitSession
from apps.visits.services import process_checkin


@pytest.mark.django_db
def test_non_staff_cannot_use_management_api(auth_client):
    response = auth_client.get("/api/v1/management/dashboard/summary")

    assert response.status_code == 403


@pytest.mark.django_db
def test_staff_can_trace_same_event_by_user_card_and_spot(staff_client, accepted_event):
    user_events = staff_client.get(
        f"/api/v1/management/users/{accepted_event.user_id}/checkins"
    ).json()["data"]["items"]
    card_events = staff_client.get(
        f"/api/v1/management/cards/{accepted_event.card_id}/checkins"
    ).json()["data"]["items"]
    spot_events = staff_client.get(
        f"/api/v1/management/spots/{accepted_event.spot_id}/checkins"
    ).json()["data"]["items"]

    assert {user_events[0]["id"], card_events[0]["id"], spot_events[0]["id"]} == {
        str(accepted_event.id)
    }


@pytest.mark.django_db
def test_management_user_and_card_lists_hide_sensitive_values(
    staff_client,
    user,
    bound_cards,
):
    user.wechat_openid = "openid-must-not-leak"
    user.save(update_fields=("wechat_openid",))

    users = staff_client.get("/api/v1/management/users")
    cards = staff_client.get("/api/v1/management/cards")

    assert users.status_code == cards.status_code == 200
    assert "openid-must-not-leak" not in str(users.json())
    assert bound_cards[0].plain_uid not in str(cards.json())
    assert cards.json()["data"]["items"][0]["uid_masked"].startswith("****")


@pytest.mark.django_db
def test_dashboard_counts_distinct_visitors_and_active_bindings(
    staff_client,
    accepted_event,
    bound_cards,
    scene,
):
    response = staff_client.get(f"/api/v1/management/dashboard/summary?scene_id={scene.id}")

    data = response.json()["data"]
    assert response.status_code == 200
    assert data["today_visitors"] == 1
    assert data["accepted_checkins"] == 1
    assert data["bound_cards"] == 2
    assert data["scene_id"] == str(scene.id)
    assert data["generated_at"]


@pytest.mark.django_db
def test_spot_statistics_separate_visitors_from_event_count(
    staff_client,
    accepted_event,
    device,
    bound_cards,
):
    process_checkin(
        device=device,
        payload={
            "event_id": "management-event-2",
            "spot_id": device.spot_id,
            "card_uid": bound_cards[1].plain_uid,
            "checkin_type": "rfid",
        },
    )

    response = staff_client.get(f"/api/v1/management/spots/{accepted_event.spot_id}/statistics")

    assert response.status_code == 200
    assert response.json()["data"]["visitor_count"] == 1
    assert response.json()["data"]["event_count"] == 2


@pytest.mark.django_db
def test_checkin_list_filters_scene_status_spot_device_card_and_user(
    staff_client,
    accepted_event,
):
    query = (
        f"scene_id={accepted_event.spot.scene_id}"
        f"&status={CheckinEvent.Status.ACCEPTED}"
        f"&spot_id={accepted_event.spot_id}"
        f"&device_id={accepted_event.device_id}"
        f"&card_id={accepted_event.card_id}"
        f"&user_id={accepted_event.user_id}"
    )
    response = staff_client.get(f"/api/v1/management/checkins?{query}")

    assert response.status_code == 200
    assert [item["id"] for item in response.json()["data"]["items"]] == [str(accepted_event.id)]


@pytest.mark.django_db
def test_management_scene_and_spot_details_include_editable_fields(
    staff_client,
    scene,
    spot,
):
    scene.map_image_url = "https://example.com/jiang-an.webp"
    scene.save(update_fields=("map_image_url",))
    media = SpotMedia.objects.create(
        spot=spot,
        url="https://example.com/library.webp",
        caption="江安图书馆",
    )

    scene_response = staff_client.get(f"/api/v1/management/scenes/{scene.id}")
    spot_response = staff_client.get(f"/api/v1/management/spots/{spot.id}")

    assert scene_response.json()["data"]["map_image_url"].endswith("jiang-an.webp")
    data = spot_response.json()["data"]
    assert data["map_x"] == str(spot.map_x)
    assert data["map_y"] == str(spot.map_y)
    assert data["summary"] == spot.summary
    assert data["description"] == spot.description
    assert data["knowledge_content"] == spot.knowledge_content
    assert data["tags"] == spot.tags
    assert data["media"][0]["id"] == str(media.id)


@pytest.mark.django_db
def test_management_binding_history_includes_unbound_reason(
    staff_client,
    user,
    bound_cards,
):
    binding = CardBinding.objects.get(card=bound_cards[0])
    binding.unbound_at = timezone.now()
    binding.unbound_reason = "用户报告卡片遗失"
    binding.save(update_fields=("unbound_at", "unbound_reason"))

    response = staff_client.get(f"/api/v1/management/users/{user.id}/cards")

    item = next(row for row in response.json()["data"]["items"] if row["id"] == str(binding.id))
    assert item["unbound_reason"] == "用户报告卡片遗失"


@pytest.mark.django_db
def test_management_device_card_and_user_lists_apply_filters(
    staff_client,
    device,
    scene,
    spot,
    user,
    bound_cards,
):
    Device.objects.create(
        device_id="SCU-JA-OTHER-DEVICE",
        scene=scene,
        spot=spot,
        device_type=Device.DeviceType.RFID,
        secret_encrypted="unused-in-management-test",
        secret_fingerprint="other001",
        status=Device.Status.DISABLED,
    )
    bound_cards[1].status = Card.Status.DISABLED
    bound_cards[1].save(update_fields=("status",))
    get_user_model().objects.create_user(username="another-visitor", is_demo=True)

    devices = staff_client.get(
        "/api/v1/management/devices",
        {
            "scene_id": str(scene.id),
            "spot_id": str(spot.id),
            "search": device.device_id,
            "status": Device.Status.ACTIVE,
        },
    ).json()["data"]["items"]
    cards = staff_client.get(
        "/api/v1/management/cards",
        {"search": bound_cards[0].serial_no, "status": Card.Status.ACTIVE},
    ).json()["data"]["items"]
    users = staff_client.get(
        "/api/v1/management/users",
        {"search": user.username, "is_active": "true", "is_demo": "false"},
    ).json()["data"]["items"]

    assert [row["id"] for row in devices] == [str(device.id)]
    assert [row["id"] for row in cards] == [str(bound_cards[0].id)]
    assert [row["id"] for row in users] == [str(user.id)]


@pytest.mark.django_db
def test_management_boolean_filter_rejects_invalid_values(staff_client):
    response = staff_client.get("/api/v1/management/users", {"is_demo": "maybe"})

    assert response.status_code == 400
    assert response.json()["error"]["details"]["is_demo"] == "必须为 true 或 false"


@pytest.mark.django_db
def test_management_spot_and_route_lists_apply_filters(staff_client, scene, spot):
    Spot.objects.create(
        scene=scene,
        slug="other-spot",
        name="其他点位",
        category="landmark",
        map_x="0.8",
        map_y="0.8",
        status=PublishStatus.DRAFT,
    )
    target_route = Route.objects.create(
        scene=scene,
        slug="jiang-an-classic",
        name="江安经典路线",
        estimated_minutes=90,
        status=PublishStatus.PUBLISHED,
    )
    Route.objects.create(
        scene=scene,
        slug="other-route",
        name="其他路线",
        estimated_minutes=30,
        status=PublishStatus.DRAFT,
    )

    spots = staff_client.get(
        "/api/v1/management/spots",
        {
            "scene_id": str(scene.id),
            "search": spot.slug,
            "status": PublishStatus.PUBLISHED,
        },
    ).json()["data"]["items"]
    routes = staff_client.get(
        "/api/v1/management/routes",
        {
            "scene_id": str(scene.id),
            "search": target_route.slug,
            "status": PublishStatus.PUBLISHED,
        },
    ).json()["data"]["items"]

    assert [row["id"] for row in spots] == [str(spot.id)]
    assert [row["id"] for row in routes] == [str(target_route.id)]


@pytest.mark.django_db
def test_management_visit_and_checkin_lists_apply_filters(staff_client, accepted_event):
    other_visit = VisitSession.objects.create(
        user=accepted_event.user,
        scene=accepted_event.spot.scene,
        local_date=accepted_event.visit_session.local_date + timedelta(days=1),
        started_at=timezone.now() + timedelta(days=1),
        last_checkin_at=timezone.now() + timedelta(days=1),
    )
    other_event = CheckinEvent.objects.create(
        event_id="management-filter-other",
        device=accepted_event.device,
        spot=accepted_event.spot,
        user=accepted_event.user,
        card=accepted_event.card,
        card_binding=accepted_event.card_binding,
        visit_session=other_visit,
        card_uid_hmac=accepted_event.card_uid_hmac,
        checkin_type=CheckinEvent.CheckinType.NFC,
        status=CheckinEvent.Status.ACCEPTED,
    )

    visits = staff_client.get(
        "/api/v1/management/visits",
        {
            "user_id": str(accepted_event.user_id),
            "date_from": str(accepted_event.visit_session.local_date),
            "date_to": str(accepted_event.visit_session.local_date),
        },
    ).json()["data"]["items"]
    events = staff_client.get(
        "/api/v1/management/checkins",
        {
            "visit_id": str(accepted_event.visit_session_id),
            "checkin_type": CheckinEvent.CheckinType.RFID,
        },
    ).json()["data"]["items"]

    assert [row["id"] for row in visits] == [str(accepted_event.visit_session_id)]
    assert [row["id"] for row in events] == [str(accepted_event.id)]
    assert str(other_event.id) not in {row["id"] for row in events}


@pytest.mark.django_db
def test_dashboard_ranking_and_device_status_are_scoped(staff_client, accepted_event):
    other_scene = Scene.objects.create(slug="other-campus", name="其他校区")
    other_spot = Spot.objects.create(
        scene=other_scene,
        slug="other-landmark",
        name="其他景点",
        category="landmark",
        map_x="0.5",
        map_y="0.5",
        status=PublishStatus.PUBLISHED,
    )
    other_device = Device.objects.create(
        device_id="OTHER-CAMPUS-DEVICE",
        scene=other_scene,
        spot=other_spot,
        device_type=Device.DeviceType.RFID,
        secret_encrypted="unused-in-management-test",
        secret_fingerprint="other002",
    )
    CheckinEvent.objects.create(
        event_id="other-scene-event",
        device=other_device,
        spot=other_spot,
        checkin_type=CheckinEvent.CheckinType.RFID,
        status=CheckinEvent.Status.ACCEPTED,
    )
    old_event = CheckinEvent.objects.create(
        event_id="old-target-scene-event",
        device=accepted_event.device,
        spot=accepted_event.spot,
        checkin_type=CheckinEvent.CheckinType.RFID,
        status=CheckinEvent.Status.ACCEPTED,
    )
    CheckinEvent.objects.filter(id=old_event.id).update(
        received_at=accepted_event.received_at - timedelta(days=2)
    )
    target_date = timezone.localtime(accepted_event.received_at).date()

    ranking = staff_client.get(
        "/api/v1/management/dashboard/spot-ranking",
        {
            "scene_id": str(accepted_event.spot.scene_id),
            "date_from": str(target_date),
            "date_to": str(target_date),
        },
    ).json()["data"]["items"]
    devices = staff_client.get(
        "/api/v1/management/dashboard/device-status",
        {"scene_id": str(accepted_event.spot.scene_id)},
    ).json()["data"]["items"]

    target = next(row for row in ranking if row["spot_id"] == str(accepted_event.spot_id))
    assert target["event_count"] == 1
    assert str(other_spot.id) not in {row["spot_id"] for row in ranking}
    assert [row["id"] for row in devices] == [str(accepted_event.device_id)]
