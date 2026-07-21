import pytest

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
