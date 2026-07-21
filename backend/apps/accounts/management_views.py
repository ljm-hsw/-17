import secrets

from django.db import transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAdminUser

from apps.common.api import api_response
from apps.common.audit import record_audit
from apps.common.management import (
    boolean_query_param,
    list_response,
    require_confirmed_reason,
)
from apps.common.permissions import HasManagementModelPermission
from apps.common.schema import SchemaAPIView as APIView

from .models import Card, CardActivationCode, CardBinding, User
from .services import unbind_card
from .uid import digest_card_uid, mask_card_uid, normalize_card_uid


def user_data(user):
    return {
        "id": str(user.id),
        "username": user.username,
        "nickname": user.nickname,
        "avatar_url": user.avatar_url,
        "is_demo": user.is_demo,
        "is_active": user.is_active,
        "active_card_count": sum(
            binding.unbound_at is None for binding in user.card_bindings.all()
        ),
    }


def card_data(card):
    return {
        "id": str(card.id),
        "serial_no": card.serial_no,
        "uid_masked": card.uid_masked,
        "status": card.status,
        "issued_at": card.issued_at,
        "last_used_at": card.last_used_at,
    }


def binding_data(binding):
    return {
        "id": str(binding.id),
        "user_id": str(binding.user_id),
        "card_id": str(binding.card_id),
        "alias": binding.alias,
        "is_primary": binding.is_primary,
        "bind_method": binding.bind_method,
        "bound_at": binding.bound_at,
        "unbound_at": binding.unbound_at,
        "unbound_reason": binding.unbound_reason,
    }


class UserListView(APIView):
    permission_classes = [IsAdminUser]

    @extend_schema(operation_id="management_users_list")
    def get(self, request):
        users = User.objects.prefetch_related("card_bindings").order_by("date_joined")
        search = request.query_params.get("search")
        if search:
            users = users.filter(Q(username__icontains=search) | Q(nickname__icontains=search))
        for parameter in ("is_active", "is_demo"):
            value = boolean_query_param(request, parameter)
            if value is not None:
                users = users.filter(**{parameter: value})
        return list_response(request, users, user_data)


class UserDetailView(APIView):
    permission_classes = [IsAdminUser]

    @extend_schema(operation_id="management_users_retrieve")
    def get(self, request, user_id):
        user = get_object_or_404(User.objects.prefetch_related("card_bindings"), id=user_id)
        return api_response(request, user_data(user))


class UserCardListView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request, user_id):
        get_object_or_404(User, id=user_id)
        bindings = CardBinding.objects.filter(user_id=user_id).select_related("card", "user")
        return list_response(
            request,
            bindings,
            lambda item: {**binding_data(item), "card": card_data(item.card)},
        )


class CardListView(APIView):
    permission_classes = [HasManagementModelPermission]
    management_model = Card

    @extend_schema(operation_id="management_cards_list")
    def get(self, request):
        cards = Card.objects.order_by("serial_no")
        search = request.query_params.get("search")
        if search:
            cards = cards.filter(
                Q(serial_no__icontains=search) | Q(uid_masked__icontains=search)
            )
        if request.query_params.get("status"):
            cards = cards.filter(status=request.query_params["status"])
        return list_response(request, cards, card_data)

    @transaction.atomic
    def post(self, request):
        card = _create_card(request.data)
        record_audit(
            request=request,
            action="card.create",
            target=card,
            before={},
            after=card_data(card),
        )
        return api_response(request, card_data(card), status_code=201)


class CardDetailView(APIView):
    permission_classes = [HasManagementModelPermission]
    management_model = Card

    @extend_schema(operation_id="management_cards_retrieve")
    def get(self, request, card_id):
        return api_response(request, card_data(get_object_or_404(Card, id=card_id)))

    @transaction.atomic
    def patch(self, request, card_id):
        card = get_object_or_404(Card, id=card_id)
        before = card_data(card)
        for field in ("serial_no", "status"):
            if field in request.data:
                setattr(card, field, request.data[field])
        card.full_clean(exclude=("uid_hmac", "uid_masked"))
        card.save()
        record_audit(
            request=request,
            action="card.update",
            target=card,
            before=before,
            after=card_data(card),
        )
        return api_response(request, card_data(card))


class CardBindingListView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request, card_id):
        get_object_or_404(Card, id=card_id)
        bindings = CardBinding.objects.filter(card_id=card_id).select_related("user", "card")
        return list_response(request, bindings, binding_data)


def _create_card(row):
    serial_no = str(row.get("serial_no", "")).strip()
    try:
        normalized_uid = normalize_card_uid(str(row.get("card_uid", "")))
    except ValueError as exc:
        raise ValidationError({"card_uid": "卡片 UID 格式不正确"}) from exc
    if not serial_no:
        raise ValidationError({"serial_no": "卡片编号不能为空"})
    if Card.objects.filter(serial_no=serial_no).exists():
        raise ValidationError({"serial_no": "卡片编号已存在"})
    uid_hmac = digest_card_uid(normalized_uid)
    if Card.objects.filter(uid_hmac=uid_hmac).exists():
        raise ValidationError({"card_uid": "卡片 UID 已存在"})
    return Card.objects.create(
        serial_no=serial_no,
        uid_hmac=uid_hmac,
        uid_masked=mask_card_uid(normalized_uid),
        status=Card.Status.AVAILABLE,
    )


def _preview_rows(rows):
    if not isinstance(rows, list) or len(rows) > 500:
        raise ValidationError({"rows": "必须提供不超过 500 行的数据"})
    valid, duplicate, invalid = [], [], []
    seen_serials, seen_uids = set(), set()
    for index, row in enumerate(rows):
        serial_no = str(row.get("serial_no", "")).strip() if isinstance(row, dict) else ""
        try:
            normalized_uid = normalize_card_uid(str(row.get("card_uid", "")))
        except (AttributeError, ValueError):
            invalid.append({"index": index, "serial_no": serial_no, "reason": "格式不正确"})
            continue
        uid_hmac = digest_card_uid(normalized_uid)
        if not serial_no:
            invalid.append({"index": index, "serial_no": serial_no, "reason": "编号为空"})
        elif (
            serial_no in seen_serials
            or uid_hmac in seen_uids
            or Card.objects.filter(serial_no=serial_no).exists()
            or Card.objects.filter(uid_hmac=uid_hmac).exists()
        ):
            duplicate.append(
                {
                    "index": index,
                    "serial_no": serial_no,
                    "uid_masked": mask_card_uid(normalized_uid),
                }
            )
        else:
            valid.append(
                {
                    "index": index,
                    "serial_no": serial_no,
                    "uid_masked": mask_card_uid(normalized_uid),
                }
            )
        seen_serials.add(serial_no)
        seen_uids.add(uid_hmac)
    return {"valid": valid, "duplicate": duplicate, "invalid": invalid}


class CardImportPreviewView(APIView):
    permission_classes = [HasManagementModelPermission]
    management_model = Card

    def post(self, request):
        return api_response(request, _preview_rows(request.data.get("rows")))


class CardImportConfirmView(APIView):
    permission_classes = [HasManagementModelPermission]
    management_model = Card

    @transaction.atomic
    def post(self, request):
        if request.data.get("confirm") is not True:
            raise ValidationError({"confirm": "必须确认导入"})
        rows = request.data.get("rows")
        preview = _preview_rows(rows)
        if preview["duplicate"] or preview["invalid"]:
            raise ValidationError({"rows": preview})
        results = []
        for row in rows:
            card = _create_card(row)
            result = card_data(card)
            results.append(result)
            record_audit(
                request=request,
                action="card.import",
                target=card,
                before={},
                after=result,
            )
        return api_response(request, {"items": results})


class ActivationCodeCreateView(APIView):
    permission_classes = [HasManagementModelPermission]
    management_model = CardActivationCode

    @transaction.atomic
    def post(self, request, card_id):
        card = get_object_or_404(Card, id=card_id)
        plaintext = secrets.token_urlsafe(6).replace("-", "").replace("_", "")[:8].upper()
        code = CardActivationCode(card=card)
        code.set_code(plaintext)
        code.save()
        record_audit(
            request=request,
            action="card.activation_code.create",
            target=code,
            before={},
            after={"card_id": str(card.id), "status": code.status},
        )
        return api_response(
            request,
            {"id": str(code.id), "card_id": str(card.id), "activation_code": plaintext},
            status_code=201,
        )


class ForceUnbindView(APIView):
    permission_classes = [HasManagementModelPermission]
    management_model = CardBinding
    permission_action = "change"

    @transaction.atomic
    def post(self, request, binding_id):
        reason = require_confirmed_reason(request.data)
        binding = get_object_or_404(
            CardBinding.objects.select_related("card", "user"),
            id=binding_id,
            unbound_at__isnull=True,
        )
        before = binding_data(binding)
        binding = unbind_card(user=binding.user, binding=binding, reason=reason)
        after = binding_data(binding)
        record_audit(
            request=request,
            action="binding.force_unbind",
            target=binding,
            before=before,
            after=after,
            reason=reason,
        )
        return api_response(request, after)
