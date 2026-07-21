import secrets

from django.db import transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema
from rest_framework.exceptions import ValidationError

from apps.common.api import api_response
from apps.common.audit import record_audit
from apps.common.management import list_response, require_confirmed_reason
from apps.common.permissions import HasManagementModelPermission
from apps.common.schema import SchemaAPIView as APIView
from apps.scenes.models import Scene, Spot

from .crypto import encrypt_device_secret, fingerprint_device_secret
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
    permission_classes = [HasManagementModelPermission]
    management_model = Device

    @extend_schema(operation_id="management_devices_list")
    def get(self, request):
        devices = Device.objects.select_related("scene", "spot")
        for parameter in ("scene_id", "spot_id", "status"):
            if request.query_params.get(parameter):
                devices = devices.filter(**{parameter: request.query_params[parameter]})
        search = request.query_params.get("search")
        if search:
            devices = devices.filter(
                Q(device_id__icontains=search) | Q(firmware_version__icontains=search)
            )
        return list_response(request, devices, device_data)

    @transaction.atomic
    def post(self, request):
        scene, spot = _scene_and_spot(request.data)
        secret = _new_secret()
        device = Device.objects.create(
            device_id=request.data.get("device_id", ""),
            scene=scene,
            spot=spot,
            device_type=request.data.get("device_type", Device.DeviceType.RFID),
            secret_encrypted=encrypt_device_secret(secret),
            secret_fingerprint=fingerprint_device_secret(secret),
            status=request.data.get("status", Device.Status.ACTIVE),
            firmware_version=request.data.get("firmware_version", ""),
        )
        data = device_data(device)
        record_audit(
            request=request,
            action="device.create",
            target=device,
            before={},
            after=data,
        )
        return api_response(request, {**data, "device_secret": secret}, status_code=201)


class DeviceDetailView(APIView):
    permission_classes = [HasManagementModelPermission]
    management_model = Device

    @extend_schema(operation_id="management_devices_retrieve")
    def get(self, request, device_id):
        device = get_object_or_404(Device.objects.select_related("scene", "spot"), id=device_id)
        return api_response(request, device_data(device))

    @transaction.atomic
    def patch(self, request, device_id):
        device = get_object_or_404(Device, id=device_id)
        before = device_data(device)
        if "scene_id" in request.data or "spot_id" in request.data:
            scene, spot = _scene_and_spot(
                {
                    "scene_id": request.data.get("scene_id", device.scene_id),
                    "spot_id": request.data.get("spot_id", device.spot_id),
                }
            )
            device.scene = scene
            device.spot = spot
        for field in ("device_id", "device_type", "status", "firmware_version"):
            if field in request.data:
                setattr(device, field, request.data[field])
        device.save()
        data = device_data(device)
        record_audit(
            request=request,
            action="device.update",
            target=device,
            before=before,
            after=data,
        )
        return api_response(request, data)


def _scene_and_spot(data):
    scene = get_object_or_404(Scene, id=data.get("scene_id"))
    spot = get_object_or_404(Spot, id=data.get("spot_id"))
    if spot.scene_id != scene.id:
        raise ValidationError({"spot_id": "设备点位必须属于所选场景"})
    return scene, spot


def _new_secret():
    return secrets.token_urlsafe(32)


class DeviceRotateSecretView(APIView):
    permission_classes = [HasManagementModelPermission]
    management_model = Device
    permission_action = "change"

    @transaction.atomic
    def post(self, request, device_id):
        reason = require_confirmed_reason(request.data)
        device = get_object_or_404(Device.objects.select_for_update(), id=device_id)
        before = device_data(device)
        secret = _new_secret()
        device.secret_encrypted = encrypt_device_secret(secret)
        device.secret_fingerprint = fingerprint_device_secret(secret)
        device.save(update_fields=("secret_encrypted", "secret_fingerprint", "updated_at"))
        data = device_data(device)
        record_audit(
            request=request,
            action="device.rotate_secret",
            target=device,
            before=before,
            after=data,
            reason=reason,
        )
        return api_response(request, {**data, "device_secret": secret})
