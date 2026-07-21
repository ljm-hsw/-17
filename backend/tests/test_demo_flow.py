from io import StringIO

import pytest
from django.contrib.auth import get_user_model
from django.core.management import call_command
from drf_spectacular.generators import SchemaGenerator
from rest_framework.test import APIClient

from apps.accounts.models import Card, CardBinding
from apps.iot.models import Device
from apps.scenes.models import Route, Scene, Spot
from apps.visits.models import CheckinEvent, VisitSession
from tests.factories import SignedDeviceClient

DEMO_UIDS = {
    "SCU-JA-0001": "04A1B2C3",
    "SCU-JA-0002": "04D4E5F6",
}


@pytest.mark.django_db
def test_seed_command_is_idempotent():
    output = StringIO()
    call_command("seed_jiang_an_demo", device_secret="demo-device-secret", stdout=output)
    call_command("seed_jiang_an_demo", device_secret="demo-device-secret", stdout=output)

    assert Scene.objects.filter(slug="jiang-an-campus").count() == 1
    assert Spot.objects.filter(scene__slug="jiang-an-campus").count() == 8
    assert Route.objects.filter(scene__slug="jiang-an-campus").count() == 2
    assert Card.objects.filter(serial_no__startswith="SCU-JA-").count() == 3
    assert Device.objects.filter(device_id="SCU-JA-DEMO-001").count() == 1
    assert output.getvalue().count("设备密钥（仅显示一次）") == 1


@pytest.mark.django_db
def test_demo_flow_joins_two_cards_and_keeps_event_traceability():
    call_command("seed_jiang_an_demo", device_secret="demo-device-secret", stdout=StringIO())
    user = get_user_model().objects.create_user(username="demo-visitor")
    visitor = APIClient()
    visitor.force_authenticate(user)
    cards = []
    for serial_no, raw_uid in DEMO_UIDS.items():
        card = Card.objects.get(serial_no=serial_no)
        card.plain_uid = raw_uid
        cards.append(card)
        response = visitor.post(
            "/api/v1/me/cards/bind",
            {"card_uid": raw_uid, "bind_method": "nfc"},
            format="json",
        )
        assert response.status_code == 201

    scene = Scene.objects.get(slug="jiang-an-campus")
    library = Spot.objects.get(scene=scene, slug="jiang-an-library")
    lake = Spot.objects.get(scene=scene, slug="mingyuan-lake")
    device = Device.objects.get(device_id="SCU-JA-DEMO-001")
    signed = SignedDeviceClient("demo-device-secret")

    first = signed.post_checkin(device=device, card=cards[0], event_id="demo-event-1")
    device.spot = lake
    device.save(update_fields=("spot", "updated_at"))
    second = signed.post_checkin(device=device, card=cards[1], event_id="demo-event-2")
    duplicate = signed.post_checkin(device=device, card=cards[1], event_id="demo-event-2")
    home = visitor.get(f"/api/v1/me/home?scene={scene.slug}").json()["data"]

    assert first.status_code == second.status_code == duplicate.status_code == 200
    assert second.json()["data"] == duplicate.json()["data"]
    assert home["active_card_count"] == 2
    assert home["visit"]["checked_spot_count"] == 2
    assert VisitSession.objects.filter(user=user, scene=scene).count() == 1
    assert CheckinEvent.objects.filter(user=user).count() == 2
    assert CardBinding.objects.filter(user=user, unbound_at__isnull=True).count() == 2

    event = CheckinEvent.objects.get(event_id="demo-event-1")
    assert event.spot == library
    admin = get_user_model().objects.create_superuser(username="admin", password="demo")
    management = APIClient()
    management.force_authenticate(admin)
    user_items = management.get(f"/api/v1/management/users/{user.id}/checkins").json()["data"][
        "items"
    ]
    card_items = management.get(f"/api/v1/management/cards/{cards[0].id}/checkins").json()["data"][
        "items"
    ]
    spot_items = management.get(f"/api/v1/management/spots/{library.id}/checkins").json()["data"][
        "items"
    ]
    assert str(event.id) in {item["id"] for item in user_items}
    assert str(event.id) in {item["id"] for item in card_items}
    assert str(event.id) in {item["id"] for item in spot_items}


@pytest.mark.django_db
def test_openapi_contains_public_device_and_management_contracts():
    schema = SchemaGenerator().get_schema(request=None, public=True)

    assert "/api/v1/me/home" in schema["paths"]
    assert "/api/v1/iot/checkins" in schema["paths"]
    assert "/api/v1/management/devices/{device_id}/rotate-secret" in schema["paths"]
    assert "DeviceHMAC" in schema["components"]["securitySchemes"]
