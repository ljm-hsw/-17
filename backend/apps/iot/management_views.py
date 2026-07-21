from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAdminUser
from rest_framework.views import APIView

from apps.common.api import api_response
from apps.common.management import list_response

from .models import Device


def device_data(device):
    return {
        "id": str(device.id),
        "device_id": device.device_id,
        "scene_id": str(device.scene_id),
        "spot_id": str(device.spot_id),
        "device_type": device.device_type,
        "secret_fingerprint": device.secret_fingerprint,
        "status": device.status,
        "firmware_version": device.firmware_version,
        "last_seen_at": device.last_seen_at,
        "last_error_code": device.last_error_code,
    }


class DeviceListView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        devices = Device.objects.select_related("scene", "spot")
        if request.query_params.get("scene_id"):
            devices = devices.filter(scene_id=request.query_params["scene_id"])
        return list_response(request, devices, device_data)


class DeviceDetailView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request, device_id):
        device = get_object_or_404(Device.objects.select_related("scene", "spot"), id=device_id)
        return api_response(request, device_data(device))
