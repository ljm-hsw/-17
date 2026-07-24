import hashlib
import hmac
import json
import time
import uuid

from rest_framework.test import APIClient


def make_signature(secret, method, path, timestamp, nonce, raw_body):
    body_hash = hashlib.sha256(raw_body).hexdigest()
    canonical = "\n".join((method, path, timestamp, nonce, body_hash))
    return hmac.new(secret.encode(), canonical.encode(), hashlib.sha256).hexdigest()


class SignedDeviceClient:
    def __init__(self, secret):
        self.secret = secret
        self.client = APIClient()

    def post_signed(
        self,
        path,
        payload,
        *,
        device,
        secret=None,
        timestamp=None,
        nonce=None,
    ):
        raw_body = json.dumps(payload, separators=(",", ":")).encode()
        timestamp = str(timestamp if timestamp is not None else int(time.time()))
        nonce = nonce or uuid.uuid4().hex
        signature = make_signature(
            secret or self.secret,
            "POST",
            path,
            timestamp,
            nonce,
            raw_body,
        )
        return self.client.generic(
            "POST",
            path,
            raw_body,
            content_type="application/json",
            HTTP_X_DEVICE_ID=device.device_id,
            HTTP_X_TIMESTAMP=timestamp,
            HTTP_X_NONCE=nonce,
            HTTP_X_SIGNATURE=signature,
        )

    def post_checkin(
        self,
        *,
        device,
        card,
        event_id,
        spot=None,
        device_time=None,
    ):
        payload = {
            "event_id": event_id,
            "spot_id": str((spot or device.spot).id),
            "card_uid": card.plain_uid,
            "checkin_type": "rfid",
        }
        if device_time is not None:
            payload["device_time"] = device_time
        return self.post_signed(
            "/api/v1/iot/checkins",
            payload,
            device=device,
        )
