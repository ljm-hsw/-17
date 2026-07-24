import uuid

from django.contrib.auth.hashers import check_password, make_password
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    wechat_openid = models.CharField(max_length=128, unique=True, null=True, blank=True)
    nickname = models.CharField(max_length=100, blank=True)
    avatar_url = models.URLField(max_length=500, blank=True)
    is_demo = models.BooleanField(default=False)


class Card(models.Model):
    class Status(models.TextChoices):
        AVAILABLE = "available", "待绑定"
        ACTIVE = "active", "使用中"
        LOST = "lost", "已挂失"
        DISABLED = "disabled", "已停用"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    serial_no = models.CharField(max_length=64, unique=True)
    uid_hmac = models.CharField(max_length=64, unique=True)
    uid_masked = models.CharField(max_length=16)
    status = models.CharField(
        max_length=16,
        choices=Status.choices,
        default=Status.AVAILABLE,
        db_index=True,
    )
    issued_at = models.DateTimeField(null=True, blank=True)
    last_used_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("serial_no",)

    def __str__(self):
        return self.serial_no


class CardActivationCode(models.Model):
    class Status(models.TextChoices):
        UNUSED = "unused", "未使用"
        USED = "used", "已使用"
        REVOKED = "revoked", "已撤销"
        EXPIRED = "expired", "已过期"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    card = models.ForeignKey(Card, on_delete=models.PROTECT, related_name="activation_codes")
    code_hash = models.CharField(max_length=255)
    status = models.CharField(
        max_length=16,
        choices=Status.choices,
        default=Status.UNUSED,
        db_index=True,
    )
    expires_at = models.DateTimeField(null=True, blank=True)
    used_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="used_activation_codes",
        null=True,
        blank=True,
    )
    used_at = models.DateTimeField(null=True, blank=True)
    revoked_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def set_code(self, raw_code):
        self.code_hash = make_password(raw_code)

    def check_code(self, raw_code):
        return check_password(raw_code, self.code_hash)


class CardBinding(models.Model):
    class BindMethod(models.TextChoices):
        NFC = "nfc", "手机 NFC"
        MANUAL = "manual", "手动输入"
        ADMIN = "admin", "管理员"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.PROTECT, related_name="card_bindings")
    card = models.ForeignKey(Card, on_delete=models.PROTECT, related_name="bindings")
    activation_code = models.ForeignKey(
        CardActivationCode,
        on_delete=models.PROTECT,
        related_name="bindings",
        null=True,
        blank=True,
    )
    bind_method = models.CharField(
        max_length=16,
        choices=BindMethod.choices,
        default=BindMethod.MANUAL,
    )
    alias = models.CharField(max_length=80, blank=True)
    is_primary = models.BooleanField(default=False)
    bound_at = models.DateTimeField(auto_now_add=True)
    unbound_at = models.DateTimeField(null=True, blank=True)
    unbound_reason = models.CharField(max_length=300, blank=True)

    class Meta:
        ordering = ("-bound_at",)
        constraints = (
            models.UniqueConstraint(
                fields=("card",),
                condition=models.Q(unbound_at__isnull=True),
                name="uniq_active_binding_per_card",
            ),
            models.UniqueConstraint(
                fields=("user",),
                condition=models.Q(unbound_at__isnull=True, is_primary=True),
                name="uniq_primary_binding_per_user",
            ),
        )
