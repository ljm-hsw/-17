from django.conf import settings
from django.contrib.auth import authenticate
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.serializers import CharField, Serializer
from rest_framework_simplejwt.tokens import RefreshToken

from apps.common.api import api_response
from apps.common.errors import ApiError
from apps.common.schema import SchemaAPIView as APIView


class ManagementLoginSerializer(Serializer):
    username = CharField(max_length=150)
    password = CharField(max_length=128, trim_whitespace=False, write_only=True)


def management_user_data(user):
    return {
        "id": str(user.id),
        "username": user.username,
        "nickname": user.nickname,
        "is_superuser": user.is_superuser,
        "is_demo": user.is_demo,
        "permissions": sorted(user.get_all_permissions()),
    }


class ManagementLoginView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = ManagementLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = authenticate(request=request, **serializer.validated_data)
        if not user or not user.is_active or not user.is_staff:
            raise ApiError(
                code="INVALID_CREDENTIALS",
                message="用户名或密码不正确",
                status_code=401,
            )
        if user.is_demo and not settings.DEBUG:
            raise ApiError(
                code="DEMO_ACCOUNT_FORBIDDEN",
                message="演示账号不能用于生产环境",
                status_code=401,
            )

        refresh = RefreshToken.for_user(user)
        return api_response(
            request,
            {
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "user": management_user_data(user),
            },
        )


class ManagementMeView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        return api_response(request, management_user_data(request.user))
