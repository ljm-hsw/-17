from drf_spectacular.extensions import OpenApiAuthenticationExtension
from rest_framework import serializers
from rest_framework.generics import GenericAPIView


class EmptySerializer(serializers.Serializer):
    """Fallback schema for endpoints whose response is assembled by a service."""


class SchemaAPIView(GenericAPIView):
    serializer_class = EmptySerializer


class DeviceHMACAuthenticationScheme(OpenApiAuthenticationExtension):
    target_class = "apps.iot.authentication.DeviceHMACAuthentication"
    name = "DeviceHMAC"

    def get_security_definition(self, auto_schema):
        del auto_schema
        return {
            "type": "apiKey",
            "in": "header",
            "name": "X-Signature",
            "description": (
                "设备 HMAC 请求还必须同时携带 X-Device-Id、X-Timestamp、X-Nonce；"
                "签名原文见项目 API 文档。"
            ),
        }
