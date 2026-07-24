import hashlib
import hmac
import time
from datetime import timedelta

from cryptography.fernet import InvalidToken
from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from django.db import IntegrityError, transaction
from django.utils import timezone
from rest_framework.authentication import BaseAuthentication

from apps.common.errors import ApiError

from .crypto import decrypt_device_secret
from .models import Device, DeviceRequestNonce


class DeviceHMACAuthentication(BaseAuthentication):
    header_names = ("X-Device-Id", "X-Timestamp", "X-Nonce", "X-Signature")

    def authenticate(self, request):
        values = {name: request.headers.get(name, "") for name in self.header_names}
        if not all(values.values()):
            raise ApiError("DEVICE_UNAUTHORIZED", "缺少设备认证信息", 401)

        device = self._get_device(values["X-Device-Id"])
        if device.status != Device.Status.ACTIVE:
            raise ApiError("DEVICE_DISABLED", "设备已停用", 403)

        timestamp = self._validate_timestamp(values["X-Timestamp"])
        nonce = values["X-Nonce"]
        if len(nonce) > 128:
            raise ApiError("DEVICE_UNAUTHORIZED", "设备请求随机数无效", 401)

        expected = self._signature(
            device=device,
            method=request.method,
            path=request.path,
            timestamp=values["X-Timestamp"],
            nonce=nonce,
            raw_body=request.body,
        )
        if not hmac.compare_digest(expected, values["X-Signature"].lower()):
            raise ApiError("SIGNATURE_INVALID", "设备签名无效", 401)

        self._remember_nonce(device=device, nonce=nonce, timestamp=timestamp)
        return AnonymousUser(), device

    def authenticate_header(self, request):
        del request
        return "Device-HMAC"

    @staticmethod
    def _get_device(device_id):
        try:
            return Device.objects.select_related("scene", "spot").get(device_id=device_id)
        except Device.DoesNotExist as exc:
            raise ApiError("DEVICE_UNAUTHORIZED", "设备身份无效", 401) from exc

    @staticmethod
    def _validate_timestamp(raw_timestamp):
        try:
            timestamp = int(raw_timestamp)
        except ValueError as exc:
            raise ApiError("REQUEST_EXPIRED", "设备时间戳无效", 401) from exc
        if abs(int(time.time()) - timestamp) > settings.DEVICE_SIGNATURE_MAX_AGE_SECONDS:
            raise ApiError("REQUEST_EXPIRED", "设备请求已过期", 401)
        return timestamp

    @staticmethod
    def _signature(*, device, method, path, timestamp, nonce, raw_body):
        try:
            secret = decrypt_device_secret(device.secret_encrypted)
        except (InvalidToken, ValueError) as exc:
            raise ApiError("DEVICE_UNAUTHORIZED", "设备身份无效", 401) from exc
        body_hash = hashlib.sha256(raw_body).hexdigest()
        canonical = "\n".join((method.upper(), path, timestamp, nonce, body_hash))
        return hmac.new(secret.encode(), canonical.encode(), hashlib.sha256).hexdigest()

    @staticmethod
    def _remember_nonce(*, device, nonce, timestamp):
        del timestamp
        expires_at = timezone.now() + timedelta(
            seconds=settings.DEVICE_SIGNATURE_MAX_AGE_SECONDS,
        )
        try:
            with transaction.atomic():
                DeviceRequestNonce.objects.create(
                    device=device,
                    nonce=nonce,
                    expires_at=expires_at,
                )
        except IntegrityError as exc:
            raise ApiError("NONCE_REPLAYED", "设备请求不可重复提交", 401) from exc
