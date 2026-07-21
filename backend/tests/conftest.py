import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from apps.accounts.models import Card, CardBinding
from apps.accounts.uid import digest_card_uid, mask_card_uid
from apps.iot.crypto import encrypt_device_secret
from apps.iot.models import Device
from apps.scenes.models import Scene, Spot
from tests.factories import SignedDeviceClient

TEST_DEVICE_SECRET = "demo-device-secret"
TEST_FERNET_KEY = "MDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDA="


@pytest.fixture
def scene(db):
    return Scene.objects.create(
        slug="jiang-an-campus",
        name="四川大学江安校区",
        status="published",
    )


@pytest.fixture
def spot(scene):
    return Spot.objects.create(
        scene=scene,
        slug="library",
        name="江安图书馆",
        category="study",
        map_x="0.25000",
        map_y="0.40000",
        status="published",
    )


@pytest.fixture
def device(settings, scene, spot):
    settings.DEVICE_SECRET_ENCRYPTION_KEY = TEST_FERNET_KEY
    return Device.objects.create(
        device_id="SCU-JA-DEVICE-001",
        scene=scene,
        spot=spot,
        device_type=Device.DeviceType.RFID,
        secret_encrypted=encrypt_device_secret(TEST_DEVICE_SECRET),
        secret_fingerprint="9a4f2c1d",
    )


@pytest.fixture
def device_client():
    return SignedDeviceClient(TEST_DEVICE_SECRET)


@pytest.fixture
def user(db):
    return get_user_model().objects.create_user(username="visitor")


@pytest.fixture
def auth_client(user):
    client = APIClient()
    client.force_authenticate(user=user)
    client.user = user
    return client


@pytest.fixture
def bound_cards(user):
    cards = []
    for index, raw_uid in enumerate(("04A1B2C3", "04D4E5F6"), start=1):
        card = Card.objects.create(
            serial_no=f"SCU-JA-{index:04d}",
            uid_hmac=digest_card_uid(raw_uid),
            uid_masked=mask_card_uid(raw_uid),
            status=Card.Status.ACTIVE,
        )
        card.plain_uid = raw_uid
        CardBinding.objects.create(
            user=user,
            card=card,
            bind_method=CardBinding.BindMethod.NFC,
            is_primary=index == 1,
        )
        cards.append(card)
    return cards
