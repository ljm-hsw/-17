from django.urls import reverse


def test_health_endpoint_returns_stable_envelope(client):
    response = client.get(reverse("health"))

    assert response.status_code == 200
    assert response.json()["data"] == {"status": "ok"}
    assert response.json()["request_id"]
    assert response.headers["X-Request-ID"] == response.json()["request_id"]
