from django.db import IntegrityError, transaction
from django.utils import timezone

from apps.common.errors import ApiError

from .models import Card, CardActivationCode, CardBinding
from .uid import digest_card_uid


def _get_locked_card(card_uid):
    try:
        return Card.objects.select_for_update().get(uid_hmac=digest_card_uid(card_uid))
    except Card.DoesNotExist as exc:
        raise ApiError("CARD_NOT_FOUND", "未找到对应卡片", 404) from exc


def _get_manual_activation_code(card, raw_code):
    if not raw_code:
        raise ApiError("ACTIVATION_CODE_INVALID", "请输入卡片激活码", 400)

    codes = CardActivationCode.objects.select_for_update().filter(card=card)
    matching = next((code for code in codes if code.check_code(raw_code)), None)
    if matching is None:
        raise ApiError("ACTIVATION_CODE_INVALID", "激活码不正确", 400)
    if matching.status == CardActivationCode.Status.USED:
        raise ApiError("ACTIVATION_CODE_USED", "激活码已使用", 409)
    if matching.status != CardActivationCode.Status.UNUSED:
        raise ApiError("ACTIVATION_CODE_INVALID", "激活码不可用", 400)
    if matching.expires_at and matching.expires_at <= timezone.now():
        matching.status = CardActivationCode.Status.EXPIRED
        matching.save(update_fields=("status",))
        raise ApiError("ACTIVATION_CODE_EXPIRED", "激活码已过期", 400)
    return matching


@transaction.atomic
def bind_card(*, user, card_uid, bind_method, activation_code=None, alias=""):
    if bind_method not in {CardBinding.BindMethod.NFC, CardBinding.BindMethod.MANUAL}:
        raise ApiError("VALIDATION_ERROR", "不支持的绑卡方式", 400)

    card = _get_locked_card(card_uid)
    if card.status in {Card.Status.LOST, Card.Status.DISABLED}:
        raise ApiError("CARD_DISABLED", "卡片当前不可绑定", 409)
    if CardBinding.objects.filter(card=card, unbound_at__isnull=True).exists():
        raise ApiError("CARD_ALREADY_BOUND", "该卡片已绑定其他账号", 409)

    used_activation_code = None
    if bind_method == CardBinding.BindMethod.MANUAL:
        used_activation_code = _get_manual_activation_code(card, activation_code)

    has_primary = CardBinding.objects.filter(
        user=user,
        unbound_at__isnull=True,
        is_primary=True,
    ).exists()
    try:
        binding = CardBinding.objects.create(
            user=user,
            card=card,
            activation_code=used_activation_code,
            bind_method=bind_method,
            alias=alias,
            is_primary=not has_primary,
        )
    except IntegrityError as exc:
        raise ApiError("CARD_ALREADY_BOUND", "该卡片已绑定其他账号", 409) from exc
    if used_activation_code:
        used_activation_code.status = CardActivationCode.Status.USED
        used_activation_code.used_by = user
        used_activation_code.used_at = timezone.now()
        used_activation_code.save(update_fields=("status", "used_by", "used_at"))
    if card.status != Card.Status.ACTIVE:
        card.status = Card.Status.ACTIVE
        card.save(update_fields=("status", "updated_at"))
    return binding


@transaction.atomic
def set_primary_binding(*, user, binding):
    binding = CardBinding.objects.select_for_update().get(
        id=binding.id,
        user=user,
        unbound_at__isnull=True,
    )
    CardBinding.objects.filter(
        user=user,
        unbound_at__isnull=True,
        is_primary=True,
    ).exclude(id=binding.id).update(is_primary=False)
    if not binding.is_primary:
        binding.is_primary = True
        binding.save(update_fields=("is_primary",))
    return binding


@transaction.atomic
def unbind_card(*, user, binding, reason):
    binding = CardBinding.objects.select_for_update().select_related("card").get(
        id=binding.id,
        user=user,
        unbound_at__isnull=True,
    )
    was_primary = binding.is_primary
    binding.unbound_at = timezone.now()
    binding.unbound_reason = reason
    binding.is_primary = False
    binding.save(update_fields=("unbound_at", "unbound_reason", "is_primary"))

    binding.card.status = Card.Status.AVAILABLE
    binding.card.save(update_fields=("status", "updated_at"))
    if was_primary:
        replacement = (
            CardBinding.objects.select_for_update()
            .filter(user=user, unbound_at__isnull=True)
            .order_by("-bound_at")
            .first()
        )
        if replacement:
            replacement.is_primary = True
            replacement.save(update_fields=("is_primary",))
    return binding
