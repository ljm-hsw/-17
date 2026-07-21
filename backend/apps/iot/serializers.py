from rest_framework import serializers


class HeartbeatSerializer(serializers.Serializer):
    firmware_version = serializers.CharField(max_length=64, required=False, allow_blank=True)
    last_error_code = serializers.CharField(max_length=64, required=False, allow_blank=True)
