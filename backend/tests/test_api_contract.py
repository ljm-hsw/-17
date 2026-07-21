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
