import time

import pytest

from apps.iot.models import DeviceRequestNonce


@pytest.mark.django_db
def test_valid_heartbeat_updates_device_without_exposing_secret(device_client, device):
    response = device_client.post_signed(
        "/api/v1/iot/heartbeat",
        {"firmware_version": "1.0.0", "last_error_code": ""},
        device=device,
    )

    assert response.status_code == 200
    assert response.json()["data"] == {
        "device_id": device.device_id,
        "spot_id": str(device.spot_id),
        "feedback_code": "HEARTBEAT_ACCEPTED",
    }
    assert "secret" not in str(response.json()).lower()
    device.refresh_from_db()
    assert device.last_seen_at is not None
    assert device.firmware_version == "1.0.0"


@pytest.mark.django_db
def test_wrong_signature_is_rejected(device_client, device):
    response = device_client.post_signed(
        "/api/v1/iot/heartbeat",
        {},
        device=device,
        secret="wrong-secret",
    )

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "DEVICE_SIGNATURE_INVALID"
    assert DeviceRequestNonce.objects.count() == 0


@pytest.mark.django_db
def test_expired_timestamp_is_rejected(device_client, device):
    response = device_client.post_signed(
        "/api/v1/iot/heartbeat",
        {},
        device=device,
        timestamp=int(time.time()) - 301,
    )

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "DEVICE_TIMESTAMP_EXPIRED"


@pytest.mark.django_db
def test_repeated_nonce_is_rejected(device_client, device):
    nonce = "same-nonce"
    first = device_client.post_signed(
        "/api/v1/iot/heartbeat",
        {},
        device=device,
        nonce=nonce,
    )
    second = device_client.post_signed(
        "/api/v1/iot/heartbeat",
        {},
        device=device,
        nonce=nonce,
    )

    assert first.status_code == 200
    assert second.status_code == 401
    assert second.json()["error"]["code"] == "DEVICE_NONCE_REUSED"
    assert DeviceRequestNonce.objects.filter(device=device, nonce=nonce).count() == 1


@pytest.mark.django_db
def test_disabled_device_is_rejected(device_client, device):
    device.status = device.Status.DISABLED
    device.save(update_fields=("status",))

    response = device_client.post_signed(
        "/api/v1/iot/heartbeat",
        {},
        device=device,
    )

    assert response.status_code == 403
    assert response.json()["error"]["code"] == "DEVICE_DISABLED"


@pytest.mark.django_db
def test_heartbeat_rejects_oversized_diagnostic(device_client, device):
    response = device_client.post_signed(
        "/api/v1/iot/heartbeat",
        {"last_error_code": "E" * 65},
        device=device,
    )

    assert response.status_code == 400
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"
