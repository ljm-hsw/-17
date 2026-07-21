import pytest

from apps.visits.models import CheckinEvent
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
