from rest_framework import serializers


class HeartbeatSerializer(serializers.Serializer):
    firmware_version = serializers.CharField(max_length=64, required=False, allow_blank=True)
    last_error_code = serializers.CharField(max_length=64, required=False, allow_blank=True)


class CheckinSerializer(serializers.Serializer):
    event_id = serializers.CharField(max_length=128)
    spot_id = serializers.UUIDField()
    card_uid = serializers.CharField(max_length=64, write_only=True)
    checkin_type = serializers.ChoiceField(choices=("nfc", "rfid", "manual_admin"))
    device_time = serializers.DateTimeField(required=False, allow_null=True)
