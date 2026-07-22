import pytest


@pytest.mark.django_db
def test_local_admin_web_origin_can_preflight_management_api(client, settings):
    settings.CORS_ALLOWED_ORIGINS = ["http://localhost:5173"]
    response = client.options(
        "/api/v1/management/auth/login",
        headers={
            "origin": "http://localhost:5173",
            "access-control-request-method": "POST",
            "access-control-request-headers": "content-type",
        },
    )

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://localhost:5173"
    assert "POST" in response.headers["access-control-allow-methods"]
