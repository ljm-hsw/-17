import pytest
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.test import APIClient

from apps.accounts.models import Card, CardActivationCode, CardBinding
from apps.common.models import AuditLog
from apps.iot.crypto import decrypt_device_secret
from apps.iot.models import Device
from apps.scenes.models import PublishStatus, Route, RouteSpot, SpotMedia


@pytest.mark.django_db
def test_force_unbind_requires_confirmation_and_writes_audit(
    staff_client,
    user,
    bound_cards,
):
    binding = CardBinding.objects.get(user=user, card=bound_cards[0])

    missing_reason = staff_client.post(
        f"/api/v1/management/bindings/{binding.id}/force-unbind",
        {"confirm": True},
        format="json",
    )
    accepted = staff_client.post(
        f"/api/v1/management/bindings/{binding.id}/force-unbind",
        {"reason": "用户报告卡片遗失", "confirm": True},
        format="json",
    )

    assert missing_reason.status_code == 400
    assert accepted.status_code == 200
    binding.refresh_from_db()
    assert binding.unbound_at is not None
    assert AuditLog.objects.filter(
        actor=staff_client.user,
        action="binding.force_unbind",
        target_id=str(binding.id),
    ).exists()


@pytest.mark.django_db
def test_spot_disable_and_media_operations_are_audited(staff_client, spot):
    created = staff_client.post(
        f"/api/v1/management/spots/{spot.id}/media",
        {
            "url": "https://example.com/library.jpg",
            "caption": "图书馆",
            "sort_order": 2,
        },
        format="json",
    )
    media_id = created.json()["data"]["id"]
    reordered = staff_client.patch(
        f"/api/v1/management/spots/{spot.id}/media/{media_id}",
        {"sort_order": 1},
        format="json",
    )
    disabled_media = staff_client.post(
        f"/api/v1/management/spots/{spot.id}/media/{media_id}/disable",
        {"confirm": True, "reason": "图片版权待确认"},
        format="json",
    )
    disabled_spot = staff_client.post(
        f"/api/v1/management/spots/{spot.id}/disable",
        {"confirm": True, "reason": "点位临时维护"},
        format="json",
    )

    assert created.status_code == 201
    assert reordered.status_code == disabled_media.status_code == disabled_spot.status_code == 200
    spot.refresh_from_db()
    media = SpotMedia.objects.get(id=media_id)
    assert spot.status == media.status == PublishStatus.DISABLED
    assert AuditLog.objects.filter(action="spot.disable", target_id=str(spot.id)).exists()


@pytest.mark.django_db
def test_activation_code_plaintext_is_returned_but_never_stored(staff_client):
    card = Card.objects.create(
        serial_no="SCU-JA-CODE-001",
        uid_hmac="a" * 64,
        uid_masked="****0001",
    )

    response = staff_client.post(
        f"/api/v1/management/cards/{card.id}/activation-codes",
        {},
        format="json",
    )

    plaintext = response.json()["data"]["activation_code"]
    stored = CardActivationCode.objects.get(card=card)
    detail = staff_client.get(f"/api/v1/management/cards/{card.id}")
    assert response.status_code == 201
    assert stored.check_code(plaintext)
    assert plaintext not in stored.code_hash
    assert plaintext not in str(detail.json())


@pytest.mark.django_db
def test_card_import_preview_has_no_writes_and_confirm_masks_uids(staff_client):
    rows = [
        {"serial_no": "SCU-JA-IMPORT-001", "card_uid": "0412345678"},
        {"serial_no": "", "card_uid": "bad"},
    ]

    preview = staff_client.post(
        "/api/v1/management/cards/import-preview",
        {"rows": rows},
        format="json",
    )
    before = Card.objects.count()
    confirmed = staff_client.post(
        "/api/v1/management/cards/import-confirm",
        {"rows": [rows[0]], "confirm": True},
        format="json",
    )

    assert preview.status_code == 200
    assert len(preview.json()["data"]["valid"]) == 1
    assert len(preview.json()["data"]["invalid"]) == 1
    assert before == 0
    assert confirmed.status_code == 200
    assert Card.objects.count() == 1
    assert "0412345678" not in str(confirmed.json())


@pytest.mark.django_db
def test_device_secret_is_shown_only_on_create_and_rotation(
    staff_client,
    scene,
    spot,
):
    created = staff_client.post(
        "/api/v1/management/devices",
        {
            "device_id": "SCU-JA-DEVICE-NEW",
            "scene_id": str(scene.id),
            "spot_id": str(spot.id),
            "device_type": "rfid",
        },
        format="json",
    )
    device = Device.objects.get(device_id="SCU-JA-DEVICE-NEW")
    first_secret = created.json()["data"]["device_secret"]
    detail = staff_client.get(f"/api/v1/management/devices/{device.id}")
    rejected = staff_client.post(
        f"/api/v1/management/devices/{device.id}/rotate-secret",
        {"confirm": False, "reason": "例行轮换"},
        format="json",
    )
    rotated = staff_client.post(
        f"/api/v1/management/devices/{device.id}/rotate-secret",
        {"confirm": True, "reason": "例行轮换"},
        format="json",
    )

    second_secret = rotated.json()["data"]["device_secret"]
    device.refresh_from_db()
    assert created.status_code == 201
    assert rejected.status_code == 400
    assert rotated.status_code == 200
    assert first_secret != second_secret
    assert decrypt_device_secret(device.secret_encrypted) == second_secret
    assert first_secret not in str(detail.json())
    assert second_secret not in device.secret_encrypted


@pytest.mark.django_db
def test_route_stops_must_belong_to_the_route_scene(staff_client, scene, spot):
    from apps.scenes.models import Scene, Spot

    other_scene = Scene.objects.create(slug="other", name="其他校区")
    other_spot = Spot.objects.create(
        scene=other_scene,
        slug="other-spot",
        name="其他点位",
        category="landmark",
        map_x="0.1",
        map_y="0.1",
    )
    invalid = staff_client.post(
        "/api/v1/management/routes",
        {
            "scene_id": str(scene.id),
            "slug": "invalid-route",
            "name": "错误路线",
            "estimated_minutes": 30,
            "stops": [{"spot_id": str(other_spot.id), "order": 1}],
        },
        format="json",
    )
    valid = staff_client.post(
        "/api/v1/management/routes",
        {
            "scene_id": str(scene.id),
            "slug": "valid-route",
            "name": "正确路线",
            "estimated_minutes": 30,
            "stops": [{"spot_id": str(spot.id), "order": 1}],
        },
        format="json",
    )

    assert invalid.status_code == 400
    assert valid.status_code == 201
    route = Route.objects.get(slug="valid-route")
    assert RouteSpot.objects.filter(route=route, spot=spot, order=1).exists()


@pytest.mark.django_db
def test_staff_without_model_permission_cannot_write_but_can_read(scene):
    staff = get_user_model().objects.create_user(username="reader", is_staff=True)
    client = APIClient()
    client.force_authenticate(staff)

    reading = client.get("/api/v1/management/scenes")
    writing = client.patch(
        f"/api/v1/management/scenes/{scene.id}",
        {"name": "无权修改"},
        format="json",
    )

    assert reading.status_code == 200
    assert writing.status_code == 403


@pytest.mark.django_db
def test_audit_endpoint_is_staff_only_and_read_only(staff_client, auth_client):
    AuditLog.objects.create(
        actor=staff_client.user,
        actor_role="system_admin",
        action="demo.action",
        target_type="scenes.scene",
        target_id="demo",
        before={},
        after={},
        reason="测试",
        request_id="req_demo",
        created_at=timezone.now(),
    )

    listed = staff_client.get("/api/v1/management/audit-logs")
    mutation = staff_client.post("/api/v1/management/audit-logs", {}, format="json")
    forbidden = auth_client.get("/api/v1/management/audit-logs")

    assert listed.status_code == 200
    assert listed.json()["data"]["items"][0]["action"] == "demo.action"
    assert mutation.status_code == 405
    assert forbidden.status_code == 403
