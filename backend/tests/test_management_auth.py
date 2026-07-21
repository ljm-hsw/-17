import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.management import call_command
from django.test import override_settings
from rest_framework.test import APIClient


@pytest.mark.django_db
@override_settings(DEBUG=True)
def test_staff_can_login_and_read_management_profile():
    client = APIClient()
    user = get_user_model().objects.create_superuser(
        username="demo_admin",
        password="TravelWeave-Demo-2026!",
        nickname="演示管理员",
        is_demo=True,
    )

    response = client.post(
        "/api/v1/management/auth/login",
        {"username": "demo_admin", "password": "TravelWeave-Demo-2026!"},
        format="json",
    )

    assert response.status_code == 200
    data = response.json()["data"]
    assert data["access"] and data["refresh"]
    assert data["user"]["id"] == str(user.id)
    assert data["user"]["is_superuser"] is True
    assert isinstance(data["user"]["permissions"], list)

    client.credentials(HTTP_AUTHORIZATION=f"Bearer {data['access']}")
    profile = client.get("/api/v1/management/auth/me")

    assert profile.status_code == 200
    assert profile.json()["data"]["username"] == "demo_admin"


@pytest.mark.django_db
def test_non_staff_cannot_use_management_login(user):
    client = APIClient()
    user.set_password("valid-password-2026")
    user.save(update_fields=("password",))

    response = client.post(
        "/api/v1/management/auth/login",
        {"username": user.username, "password": "valid-password-2026"},
        format="json",
    )

    assert response.status_code == 401


@pytest.mark.django_db
@override_settings(DEBUG=False)
def test_demo_account_is_rejected_outside_debug():
    client = APIClient()
    get_user_model().objects.create_superuser(
        username="demo_admin",
        password="TravelWeave-Demo-2026!",
        is_demo=True,
    )

    response = client.post(
        "/api/v1/management/auth/login",
        {"username": "demo_admin", "password": "TravelWeave-Demo-2026!"},
        format="json",
    )

    assert response.status_code == 401


@pytest.mark.django_db
def test_demo_seed_creates_documented_admin_with_view_only_record_permissions(settings):
    settings.DEMO_ADMIN_USERNAME = "demo_admin"
    settings.DEMO_ADMIN_PASSWORD = "TravelWeave-Demo-2026!"
    settings.DEMO_ADMIN_NICKNAME = "演示管理员"

    call_command("seed_jiang_an_demo", device_secret="seed-device-secret")
    call_command("seed_jiang_an_demo", device_secret="seed-device-secret")

    users = get_user_model().objects.filter(username="demo_admin")
    assert users.count() == 1
    user = users.get()
    assert user.is_staff and user.is_superuser and user.is_demo
    assert user.nickname == "演示管理员"
    assert user.check_password("TravelWeave-Demo-2026!")

    permissions = set(
        Group.objects.get(name="data_administrator").permissions.values_list(
            "codename", flat=True
        )
    )
    assert {"view_visitsession", "view_checkinevent"} <= permissions
    assert "change_visitsession" not in permissions
    assert "change_checkinevent" not in permissions
