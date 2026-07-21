import os
import subprocess
import sys

from django.conf import settings


def test_client_request_id_is_preserved(client):
    response = client.get("/api/v1/health", HTTP_X_REQUEST_ID="req_demo_trace")

    assert response.status_code == 200
    assert response.json()["request_id"] == "req_demo_trace"
    assert response.headers["X-Request-ID"] == "req_demo_trace"


def test_unknown_api_path_uses_stable_error_envelope(client):
    response = client.get("/api/v1/not-found")

    assert response.status_code == 404
    assert response.json()["error"] == {
        "code": "RESOURCE_NOT_FOUND",
        "message": "请求的资源不存在",
        "details": {},
    }
    assert response.json()["request_id"]


def test_api_uses_jwt_authentication_and_security_settings():
    assert settings.REST_FRAMEWORK["DEFAULT_AUTHENTICATION_CLASSES"] == (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    )
    assert settings.CARD_UID_HMAC_KEY == "test-card-hmac-key"
    assert settings.DEVICE_SECRET_ENCRYPTION_KEY.startswith("MDAw")
    assert len(settings.SECRET_KEY.encode()) >= 32


def test_production_rejects_empty_device_encryption_key():
    environment = os.environ | {
        "DJANGO_SETTINGS_MODULE": "config.settings.production",
        "DJANGO_SECRET_KEY": "production-secret-key-longer-than-32-bytes",
        "DATABASE_URL": "sqlite://:memory:",
        "ALLOWED_HOSTS": "localhost",
        "CARD_UID_HMAC_KEY": "production-card-hmac-key",
        "DEVICE_SECRET_ENCRYPTION_KEY": "",
    }

    completed = subprocess.run(
        [
            sys.executable,
            "-c",
            "from django.conf import settings; print(settings.DEVICE_SECRET_ENCRYPTION_KEY)",
        ],
        check=False,
        capture_output=True,
        text=True,
        env=environment,
    )

    assert completed.returncode != 0
    assert "DEVICE_SECRET_ENCRYPTION_KEY" in completed.stderr
