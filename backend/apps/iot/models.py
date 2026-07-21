import uuid

from django.db import models


class Device(models.Model):
    class DeviceType(models.TextChoices):
        RFID = "rfid", "RFID 打卡终端"
        PHOTO = "photo", "拍照终端"
        COMBINED = "combined", "复合终端"

    class Status(models.TextChoices):
        ACTIVE = "active", "启用"
        DISABLED = "disabled", "停用"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    device_id = models.CharField(max_length=64, unique=True)
    scene = models.ForeignKey(
        "scenes.Scene",
        on_delete=models.PROTECT,
        related_name="devices",
    )
    spot = models.ForeignKey(
        "scenes.Spot",
        on_delete=models.PROTECT,
        related_name="devices",
    )
    device_type = models.CharField(max_length=16, choices=DeviceType.choices)
    secret_encrypted = models.TextField()
    secret_fingerprint = models.CharField(max_length=32)
    status = models.CharField(
        max_length=16,
        choices=Status.choices,
        default=Status.ACTIVE,
        db_index=True,
    )
    firmware_version = models.CharField(max_length=64, blank=True)
    last_seen_at = models.DateTimeField(null=True, blank=True)
    last_error_code = models.CharField(max_length=64, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("device_id",)

    def __str__(self):
        return self.device_id


class DeviceRequestNonce(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    device = models.ForeignKey(
        Device,
        on_delete=models.CASCADE,
        related_name="request_nonces",
    )
    nonce = models.CharField(max_length=128)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(db_index=True)

    class Meta:
        constraints = (
            models.UniqueConstraint(
                fields=("device", "nonce"),
                name="uniq_request_nonce_per_device",
            ),
        )
