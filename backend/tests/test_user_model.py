from django.contrib.auth import get_user_model


def test_custom_user_uses_uuid_primary_key():
    user = get_user_model()(username="owner")

    assert user._meta.label == "accounts.User"
    assert user.id.version == 4
