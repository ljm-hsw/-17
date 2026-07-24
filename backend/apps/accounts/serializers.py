from rest_framework import serializers

from .models import CardBinding, User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "nickname", "avatar_url", "is_demo")


class CardBindingSerializer(serializers.ModelSerializer):
    card_id = serializers.UUIDField(source="card.id", read_only=True)
    serial_no = serializers.CharField(source="card.serial_no", read_only=True)
    uid_masked = serializers.CharField(source="card.uid_masked", read_only=True)
    card_status = serializers.CharField(source="card.status", read_only=True)
    last_used_at = serializers.DateTimeField(source="card.last_used_at", read_only=True)

    class Meta:
        model = CardBinding
        fields = (
            "id",
            "card_id",
            "serial_no",
            "uid_masked",
            "card_status",
            "alias",
            "is_primary",
            "bound_at",
            "unbound_at",
            "last_used_at",
        )


class BindCardSerializer(serializers.Serializer):
    card_uid = serializers.CharField(max_length=64, write_only=True)
    activation_code = serializers.CharField(max_length=64, required=False, write_only=True)
    bind_method = serializers.ChoiceField(choices=("nfc", "manual"))
    alias = serializers.CharField(max_length=80, required=False, allow_blank=True)

    def validate(self, attrs):
        if attrs["bind_method"] == "manual" and not attrs.get("activation_code"):
            raise serializers.ValidationError({"activation_code": "手输 UID 时必须填写激活码"})
        return attrs


class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("nickname", "avatar_url")
