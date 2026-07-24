import hashlib

from django.conf import settings
from django.core.exceptions import ValidationError
from django.http import Http404
from django.shortcuts import get_object_or_404
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.serializers import CharField, Serializer
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework_simplejwt.tokens import RefreshToken

from apps.common.api import api_response
from apps.common.schema import SchemaAPIView as APIView

from .models import CardBinding, User
from .selectors import list_user_bindings
from .serializers import (
    BindCardSerializer,
    CardBindingSerializer,
    UserSerializer,
    UserUpdateSerializer,
)
from .services import bind_card, set_primary_binding, unbind_card
from .wechat import exchange_wechat_code


class CodeSerializer(Serializer):
    code = CharField(max_length=256)


class DevLoginSerializer(Serializer):
    username = CharField(max_length=64)


def _token_data(user):
    refresh = RefreshToken.for_user(user)
    return {"access": str(refresh.access_token), "refresh": str(refresh)}


class WechatLoginView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = CodeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        openid = exchange_wechat_code(serializer.validated_data["code"])
        username = f"wx_{hashlib.sha256(openid.encode()).hexdigest()[:24]}"
        user, _ = User.objects.get_or_create(
            wechat_openid=openid,
            defaults={"username": username},
        )
        return api_response(request, _token_data(user))


class DevLoginView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        if not settings.DEBUG:
            raise Http404
        serializer = DevLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user, _ = User.objects.get_or_create(
            username=serializer.validated_data["username"],
            defaults={"is_demo": True},
        )
        if not user.is_demo:
            user.is_demo = True
            user.save(update_fields=("is_demo",))
        return api_response(request, _token_data(user))


class RefreshView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = TokenRefreshSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return api_response(request, serializer.validated_data)


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        data = UserSerializer(request.user).data
        data["active_card_count"] = list_user_bindings(request.user).count()
        return api_response(request, data)

    def patch(self, request):
        serializer = UserUpdateSerializer(
            request.user,
            data=request.data,
            partial=True,
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return api_response(request, UserSerializer(request.user).data)


class CardBindingListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        bindings = list_user_bindings(request.user)
        data = CardBindingSerializer(bindings, many=True).data
        return api_response(request, {"items": data})

    def post(self, request):
        serializer = BindCardSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        binding = bind_card(user=request.user, **serializer.validated_data)
        return api_response(request, CardBindingSerializer(binding).data, status_code=201)


class CardBindingDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def _binding(self, request, binding_id):
        return get_object_or_404(CardBinding, id=binding_id, user=request.user)

    def patch(self, request, binding_id):
        binding = self._binding(request, binding_id)
        alias = request.data.get("alias")
        if alias is None:
            raise ValidationError({"alias": "该字段为必填项"})
        binding.alias = alias
        binding.full_clean(exclude=("activation_code",))
        binding.save(update_fields=("alias",))
        return api_response(request, CardBindingSerializer(binding).data)

    def delete(self, request, binding_id):
        binding = self._binding(request, binding_id)
        binding = unbind_card(
            user=request.user,
            binding=binding,
            reason=request.data.get("reason", "用户主动解绑"),
        )
        return api_response(request, CardBindingSerializer(binding).data)


class SetPrimaryCardView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, binding_id):
        binding = get_object_or_404(
            CardBinding,
            id=binding_id,
            user=request.user,
            unbound_at__isnull=True,
        )
        binding = set_primary_binding(user=request.user, binding=binding)
        return api_response(request, CardBindingSerializer(binding).data)
