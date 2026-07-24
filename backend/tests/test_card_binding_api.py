from unittest.mock import patch

import pytest
from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.test import override_settings
from rest_framework.test import APIClient

from apps.accounts.models import Card, CardActivationCode, CardBinding
from apps.accounts.services import bind_card
from apps.accounts.uid import digest_card_uid, mask_card_uid


def make_card(raw_uid, serial_no, activation_code=None):
    card = Card.objects.create(
        serial_no=serial_no,
        uid_hmac=digest_card_uid(raw_uid),
        uid_masked=mask_card_uid(raw_uid),
    )
    code = None
    if activation_code:
        code = CardActivationCode(card=card)
        code.set_code(activation_code)
        code.save()
    return card, code


def authenticated_client(user):
    client = APIClient()
    client.force_authenticate(user=user)
    return client


@pytest.mark.django_db
def test_manual_binding_consumes_codes_and_allows_multiple_cards():
    user = get_user_model().objects.create_user(username="visitor")
    client = authenticated_client(user)
    first, first_code = make_card("04A1B2C3", "SCU-JA-0001", "7K9M2P")
    second, second_code = make_card("04D4E5F6", "SCU-JA-0002", "8N3Q4R")

    first_response = client.post(
        "/api/v1/me/cards/bind",
        {
            "card_uid": "04A1B2C3",
            "activation_code": "7K9M2P",
            "bind_method": "manual",
            "alias": "绿色手环",
        },
        format="json",
    )
    second_response = client.post(
        "/api/v1/me/cards/bind",
        {
            "card_uid": "04D4E5F6",
            "activation_code": "8N3Q4R",
            "bind_method": "manual",
            "alias": "蓝色卡片",
        },
        format="json",
    )

    assert first_response.status_code == second_response.status_code == 201
    assert CardBinding.objects.filter(user=user, unbound_at__isnull=True).count() == 2
    assert CardBinding.objects.get(card=first).is_primary is True
    assert CardBinding.objects.get(card=second).is_primary is False
    first_code.refresh_from_db()
    second_code.refresh_from_db()
    assert first_code.status == second_code.status == "used"
    assert "04A1B2C3" not in str(first_response.json())


@pytest.mark.django_db
def test_nfc_binding_does_not_require_or_consume_activation_code():
    user = get_user_model().objects.create_user(username="visitor")
    client = authenticated_client(user)
    card, code = make_card("04A1B2C3", "SCU-JA-0001", "7K9M2P")

    response = client.post(
        "/api/v1/me/cards/bind",
        {"card_uid": "04A1B2C3", "bind_method": "nfc"},
        format="json",
    )

    assert response.status_code == 201
    assert CardBinding.objects.get(card=card).activation_code is None
    code.refresh_from_db()
    assert code.status == "unused"


@pytest.mark.django_db
def test_manual_binding_rejects_invalid_code_and_card_owned_by_another_user():
    first_user = get_user_model().objects.create_user(username="first")
    second_user = get_user_model().objects.create_user(username="second")
    card, _ = make_card("04A1B2C3", "SCU-JA-0001", "7K9M2P")
    invalid = authenticated_client(first_user).post(
        "/api/v1/me/cards/bind",
        {
            "card_uid": "04A1B2C3",
            "activation_code": "WRONG1",
            "bind_method": "manual",
        },
        format="json",
    )
    CardBinding.objects.create(user=first_user, card=card, is_primary=True)

    conflict = authenticated_client(second_user).post(
        "/api/v1/me/cards/bind",
        {"card_uid": "04A1B2C3", "bind_method": "nfc"},
        format="json",
    )

    assert invalid.status_code == 400
    assert invalid.json()["error"]["code"] == "ACTIVATION_CODE_INVALID"
    assert conflict.status_code == 409
    assert conflict.json()["error"]["code"] == "CARD_ALREADY_BOUND"


@pytest.mark.django_db
def test_manual_binding_rejects_an_activation_code_that_was_already_used():
    first_user = get_user_model().objects.create_user(username="first")
    second_user = get_user_model().objects.create_user(username="second")
    card, code = make_card("04A1B2C3", "SCU-JA-0001", "7K9M2P")
    code.status = CardActivationCode.Status.USED
    code.used_by = first_user
    code.save(update_fields=("status", "used_by"))

    response = authenticated_client(second_user).post(
        "/api/v1/me/cards/bind",
        {
            "card_uid": "04A1B2C3",
            "activation_code": "7K9M2P",
            "bind_method": "manual",
        },
        format="json",
    )

    assert response.status_code == 409
    assert response.json()["error"]["code"] == "ACTIVATION_CODE_USED"
    assert not CardBinding.objects.filter(card=card).exists()


@pytest.mark.django_db
def test_binding_integrity_race_is_reported_as_card_conflict(monkeypatch):
    user = get_user_model().objects.create_user(username="visitor")
    make_card("04A1B2C3", "SCU-JA-0001")

    def raise_integrity_error(**_kwargs):
        raise IntegrityError("concurrent active binding")

    monkeypatch.setattr(CardBinding.objects, "create", raise_integrity_error)

    with pytest.raises(Exception) as exc_info:
        bind_card(user=user, card_uid="04A1B2C3", bind_method="nfc")

    error = exc_info.value
    assert getattr(error, "code", None) == "CARD_ALREADY_BOUND"
    assert getattr(error, "status_code", None) == 409


@pytest.mark.django_db
def test_primary_switch_and_unbind_promotes_remaining_card():
    user = get_user_model().objects.create_user(username="visitor")
    client = authenticated_client(user)
    first, _ = make_card("04A1B2C3", "SCU-JA-0001")
    second, _ = make_card("04D4E5F6", "SCU-JA-0002")
    first_binding = CardBinding.objects.create(user=user, card=first, is_primary=True)
    second_binding = CardBinding.objects.create(user=user, card=second, is_primary=False)

    switch = client.post(f"/api/v1/me/cards/{second_binding.id}/set-primary")
    unbind = client.delete(
        f"/api/v1/me/cards/{second_binding.id}",
        {"reason": "更换手环"},
        format="json",
    )

    assert switch.status_code == 200
    assert unbind.status_code == 200
    first_binding.refresh_from_db()
    second_binding.refresh_from_db()
    assert second_binding.unbound_at is not None
    assert first_binding.is_primary is True


@pytest.mark.django_db
def test_unbinding_non_primary_card_keeps_primary_and_other_users_cannot_access_it():
    owner = get_user_model().objects.create_user(username="owner")
    stranger = get_user_model().objects.create_user(username="stranger")
    primary_card, _ = make_card("04A1B2C3", "SCU-JA-0001")
    secondary_card, _ = make_card("04D4E5F6", "SCU-JA-0002")
    primary = CardBinding.objects.create(user=owner, card=primary_card, is_primary=True)
    secondary = CardBinding.objects.create(
        user=owner,
        card=secondary_card,
        is_primary=False,
    )

    forbidden = authenticated_client(stranger).patch(
        f"/api/v1/me/cards/{secondary.id}",
        {"alias": "不属于我的卡"},
        format="json",
    )
    unbound = authenticated_client(owner).delete(f"/api/v1/me/cards/{secondary.id}")

    primary.refresh_from_db()
    secondary.refresh_from_db()
    assert forbidden.status_code == 404
    assert unbound.status_code == 200
    assert primary.is_primary is True
    assert secondary.unbound_at is not None


@pytest.mark.django_db
@override_settings(DEBUG=True)
def test_dev_login_is_available_only_in_debug():
    response = APIClient().post(
        "/api/v1/auth/dev-login",
        {"username": "demo-visitor"},
        format="json",
    )

    assert response.status_code == 200
    assert response.json()["data"]["access"]
    assert response.json()["data"]["refresh"]
    assert get_user_model().objects.get(username="demo-visitor").is_demo is True


@pytest.mark.django_db
def test_dev_login_is_hidden_when_debug_is_false():
    response = APIClient().post(
        "/api/v1/auth/dev-login",
        {"username": "demo-visitor"},
        format="json",
    )

    assert response.status_code == 404


@pytest.mark.django_db
def test_wechat_login_uses_exchanged_openid_without_exposing_it():
    with patch("apps.accounts.views.exchange_wechat_code", return_value="openid-secret-value"):
        response = APIClient().post(
            "/api/v1/auth/wechat/login",
            {"code": "temporary-code"},
            format="json",
        )

    assert response.status_code == 200
    assert response.json()["data"]["access"]
    assert "openid-secret-value" not in str(response.json())


@pytest.mark.django_db
@override_settings(DEBUG=True)
def test_refresh_and_me_endpoints_use_backend_tokens():
    client = APIClient()
    login = client.post(
        "/api/v1/auth/dev-login",
        {"username": "demo-visitor"},
        format="json",
    ).json()["data"]

    refresh = client.post(
        "/api/v1/auth/refresh",
        {"refresh": login["refresh"]},
        format="json",
    )
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {login['access']}")
    me = client.get("/api/v1/me")
    updated = client.patch(
        "/api/v1/me",
        {"nickname": "小游同学"},
        format="json",
    )

    assert refresh.status_code == 200
    assert refresh.json()["data"]["access"]
    assert me.status_code == 200
    assert me.json()["data"]["active_card_count"] == 0
    assert updated.json()["data"]["nickname"] == "小游同学"


@pytest.mark.django_db
def test_card_list_and_alias_update_are_scoped_and_masked():
    user = get_user_model().objects.create_user(username="visitor")
    client = authenticated_client(user)
    card, _ = make_card("04A1B2C3", "SCU-JA-0001")
    binding = CardBinding.objects.create(user=user, card=card, is_primary=True)

    listing = client.get("/api/v1/me/cards")
    updated = client.patch(
        f"/api/v1/me/cards/{binding.id}",
        {"alias": "我的绿色手环"},
        format="json",
    )

    assert listing.status_code == 200
    assert listing.json()["data"]["items"][0]["uid_masked"] == "****B2C3"
    assert "04A1B2C3" not in str(listing.json())
    assert updated.status_code == 200
    assert updated.json()["data"]["alias"] == "我的绿色手环"
