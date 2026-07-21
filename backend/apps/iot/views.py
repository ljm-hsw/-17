from django.utils import timezone
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView

from apps.common.api import api_response
from apps.visits.services import process_checkin

from .authentication import DeviceHMACAuthentication
from .serializers import CheckinSerializer, HeartbeatSerializer


class HeartbeatView(APIView):
    authentication_classes = [DeviceHMACAuthentication]
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = HeartbeatSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        device = request.auth
        request.auth_device = device
        device.last_seen_at = timezone.now()
        update_fields = ["last_seen_at", "updated_at"]
        for field in ("firmware_version", "last_error_code"):
            if field in serializer.validated_data:
                setattr(device, field, serializer.validated_data[field])
                update_fields.append(field)
        device.save(update_fields=update_fields)
        return api_response(
            request,
            {
                "device_id": device.device_id,
                "spot_id": str(device.spot_id),
                "feedback_code": "HEARTBEAT_ACCEPTED",
            },
        )


class CheckinView(APIView):
    authentication_classes = [DeviceHMACAuthentication]
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = CheckinSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        device = request.auth
        request.auth_device = device
        result = process_checkin(device=device, payload=serializer.validated_data)
        return api_response(request, result.data)
