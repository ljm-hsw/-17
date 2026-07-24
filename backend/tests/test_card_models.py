import pytest
from django.apps import apps
from django.db import IntegrityError, transaction


def test_uid_helpers_normalize_hash_and_mask_without_plaintext(settings):
    from apps.accounts.uid import digest_card_uid, mask_card_uid, normalize_card_uid

    settings.CARD_UID_HMAC_KEY = "test-card-hmac-key"

    assert normalize_card_uid("04:a1-b2 c3") == "04A1B2C3"
    assert digest_card_uid("04:a1-b2 c3") == digest_card_uid("04A1B2C3")
    assert digest_card_uid("04A1B2C3") != "04A1B2C3"
    assert mask_card_uid("04A1B2C3") == "****B2C3"


@pytest.mark.parametrize("raw_uid", ["", "123", "1234567G", "123456789"])
def test_uid_helper_rejects_invalid_values(raw_uid):
    from apps.accounts.uid import normalize_card_uid

    with pytest.raises(ValueError, match="invalid_card_uid"):
        normalize_card_uid(raw_uid)


@pytest.mark.django_db
def test_user_can_have_multiple_active_cards_and_only_one_primary():
    User = apps.get_model("accounts", "User")
    Card = apps.get_model("accounts", "Card")
    CardBinding = apps.get_model("accounts", "CardBinding")
    user = User.objects.create_user(username="visitor")
    first = Card.objects.create(
        serial_no="SCU-JA-0001",
        uid_hmac="uid-hmac-1",
        uid_masked="****0001",
        status="active",
    )
    second = Card.objects.create(
        serial_no="SCU-JA-0002",
        uid_hmac="uid-hmac-2",
        uid_masked="****0002",
        status="active",
    )
    third = Card.objects.create(
        serial_no="SCU-JA-0003",
        uid_hmac="uid-hmac-3",
        uid_masked="****0003",
        status="active",
    )

    CardBinding.objects.create(user=user, card=first, is_primary=True)
    CardBinding.objects.create(user=user, card=second, is_primary=False)

    assert CardBinding.objects.filter(user=user, unbound_at__isnull=True).count() == 2
    with pytest.raises(IntegrityError):
        with transaction.atomic():
            CardBinding.objects.create(user=user, card=third, is_primary=True)


@pytest.mark.django_db
def test_card_cannot_have_two_active_owners():
    User = apps.get_model("accounts", "User")
    Card = apps.get_model("accounts", "Card")
    CardBinding = apps.get_model("accounts", "CardBinding")
    first_user = User.objects.create_user(username="first")
    second_user = User.objects.create_user(username="second")
    card = Card.objects.create(
        serial_no="SCU-JA-0001",
        uid_hmac="uid-hmac-1",
        uid_masked="****0001",
        status="active",
    )
    CardBinding.objects.create(user=first_user, card=card, is_primary=True)

    with pytest.raises(IntegrityError):
        with transaction.atomic():
            CardBinding.objects.create(user=second_user, card=card, is_primary=True)


@pytest.mark.django_db
def test_activation_code_is_hashed_and_verifiable():
    Card = apps.get_model("accounts", "Card")
    CardActivationCode = apps.get_model("accounts", "CardActivationCode")
    card = Card.objects.create(
        serial_no="SCU-JA-0001",
        uid_hmac="uid-hmac-1",
        uid_masked="****0001",
    )
    activation = CardActivationCode(card=card)

    activation.set_code("7K9M2P")
    activation.save()

    assert activation.code_hash != "7K9M2P"
    assert activation.check_code("7K9M2P") is True
    assert activation.check_code("WRONG1") is False
