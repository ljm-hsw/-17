import hashlib
import hmac
import re

from django.conf import settings


def normalize_card_uid(raw):
    value = re.sub(r"[\s:-]", "", raw).upper()
    if not re.fullmatch(r"[0-9A-F]+", value or ""):
        raise ValueError("invalid_card_uid")
    if not 8 <= len(value) <= 32 or len(value) % 2:
        raise ValueError("invalid_card_uid")
    return value


def digest_card_uid(raw):
    value = normalize_card_uid(raw)
    return hmac.new(
        settings.CARD_UID_HMAC_KEY.encode(),
        value.encode(),
        hashlib.sha256,
    ).hexdigest()


def mask_card_uid(raw):
    return f"****{normalize_card_uid(raw)[-4:]}"
