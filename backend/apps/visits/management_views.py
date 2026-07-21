from datetime import timedelta
from zoneinfo import ZoneInfo

from django.db.models import Count, Q
from django.db.models.functions import TruncDate
from django.shortcuts import get_object_or_404
from django.utils import timezone
from drf_spectacular.utils import extend_schema
from rest_framework.permissions import IsAdminUser

from apps.accounts.models import CardBinding, User
from apps.common.api import api_response
from apps.common.management import list_response
from apps.common.schema import SchemaAPIView as APIView
from apps.iot.management_views import device_data
from apps.iot.models import Device
from apps.scenes.models import Scene, Spot

from .models import CheckinEvent, VisitSession


def event_data(event):
    return {
        "id": str(event.id),
        "event_id": event.event_id,
        "device_id": str(event.device_id),
        "spot_id": str(event.spot_id),
        "user_id": str(event.user_id) if event.user_id else None,
        "card_id": str(event.card_id) if event.card_id else None,
        "visit_id": str(event.visit_session_id) if event.visit_session_id else None,
        "checkin_type": event.checkin_type,
        "status": event.status,
        "failure_code": event.failure_code,
        "received_at": event.received_at,
    }


def visit_data(session):
    return {
        "id": str(session.id),
        "user_id": str(session.user_id),
        "scene_id": str(session.scene_id),
        "local_date": session.local_date,
        "started_at": session.started_at,
        "last_checkin_at": session.last_checkin_at,
    }


def filtered_events(request):
    events = CheckinEvent.objects.select_related("device", "spot", "user", "card")
    filters = {
        "spot_id": "spot_id",
        "device_id": "device_id",
        "card_id": "card_id",
        "user_id": "user_id",
        "status": "status",
        "visit_id": "visit_session_id",
        "checkin_type": "checkin_type",
    }
    for parameter, field in filters.items():
        if request.query_params.get(parameter):
            events = events.filter(**{field: request.query_params[parameter]})
    if request.query_params.get("scene_id"):
        events = events.filter(spot__scene_id=request.query_params["scene_id"])
    if request.query_params.get("date_from"):
        events = events.filter(received_at__date__gte=request.query_params["date_from"])
    if request.query_params.get("date_to"):
        events = events.filter(received_at__date__lte=request.query_params["date_to"])
    return events.order_by("-received_at", "-id")


def dashboard_events(request):
    events = CheckinEvent.objects.filter(status=CheckinEvent.Status.ACCEPTED)
    if request.query_params.get("scene_id"):
        events = events.filter(spot__scene_id=request.query_params["scene_id"])
    if request.query_params.get("date_from"):
        events = events.filter(received_at__date__gte=request.query_params["date_from"])
    if request.query_params.get("date_to"):
        events = events.filter(received_at__date__lte=request.query_params["date_to"])
    return events


class CheckinListView(APIView):
    permission_classes = [IsAdminUser]

    @extend_schema(operation_id="management_checkins_list")
    def get(self, request):
        return list_response(request, filtered_events(request), event_data)


class CheckinDetailView(APIView):
    permission_classes = [IsAdminUser]

    @extend_schema(operation_id="management_checkins_retrieve")
    def get(self, request, event_id):
        event = get_object_or_404(CheckinEvent, id=event_id)
        return api_response(request, event_data(event))


class ScopedCheckinListView(APIView):
    permission_classes = [IsAdminUser]
    scope_field = None

    def get(self, request, object_id):
        events = filtered_events(request).filter(**{self.scope_field: object_id})
        return list_response(request, events, event_data)


class UserCheckinListView(ScopedCheckinListView):
    scope_field = "user_id"


class CardCheckinListView(ScopedCheckinListView):
    scope_field = "card_id"


class SpotCheckinListView(ScopedCheckinListView):
    scope_field = "spot_id"


class DeviceCheckinListView(ScopedCheckinListView):
    scope_field = "device_id"


class VisitListView(APIView):
    permission_classes = [IsAdminUser]

    @extend_schema(operation_id="management_visits_list")
    def get(self, request):
        sessions = VisitSession.objects.select_related("scene", "user")
        if request.query_params.get("scene_id"):
            sessions = sessions.filter(scene_id=request.query_params["scene_id"])
        if request.query_params.get("user_id"):
            sessions = sessions.filter(user_id=request.query_params["user_id"])
        if request.query_params.get("date_from"):
            sessions = sessions.filter(local_date__gte=request.query_params["date_from"])
        if request.query_params.get("date_to"):
            sessions = sessions.filter(local_date__lte=request.query_params["date_to"])
        return list_response(request, sessions, visit_data)


class VisitDetailView(APIView):
    permission_classes = [IsAdminUser]

    @extend_schema(operation_id="management_visits_retrieve")
    def get(self, request, visit_id):
        return api_response(request, visit_data(get_object_or_404(VisitSession, id=visit_id)))


class UserVisitListView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request, user_id):
        get_object_or_404(User, id=user_id)
        return list_response(
            request,
            VisitSession.objects.filter(user_id=user_id).select_related("scene"),
            visit_data,
        )


class DashboardSummaryView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        scene_id = request.query_params.get("scene_id")
        scene = get_object_or_404(Scene, id=scene_id) if scene_id else Scene.objects.first()
        now = timezone.now()
        local_date = now.astimezone(ZoneInfo(scene.timezone)).date() if scene else now.date()
        events = CheckinEvent.objects.filter(status=CheckinEvent.Status.ACCEPTED)
        devices = Device.objects.filter(status=Device.Status.ACTIVE)
        if scene:
            events = events.filter(spot__scene=scene)
            devices = devices.filter(scene=scene)
        date_from = request.query_params.get("date_from", str(local_date))
        date_to = request.query_params.get("date_to", str(local_date))
        ranged = events.filter(received_at__date__gte=date_from, received_at__date__lte=date_to)
        data = {
            "generated_at": now,
            "scene_id": str(scene.id) if scene else None,
            "date_from": date_from,
            "date_to": date_to,
            "today_visitors": events.filter(received_at__date=local_date)
            .values("user_id")
            .distinct()
            .count(),
            "accepted_checkins": ranged.count(),
            "bound_cards": CardBinding.objects.filter(unbound_at__isnull=True).count(),
            "online_devices": devices.filter(
                last_seen_at__gte=now - timedelta(seconds=120)
            ).count(),
        }
        return api_response(request, data)


class CheckinTrendView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        rows = (
            dashboard_events(request)
            .annotate(date=TruncDate("received_at"))
            .values("date")
            .annotate(count=Count("id"))
            .order_by("date")
        )
        return api_response(request, {"items": list(rows)})


class SpotRankingView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        events = dashboard_events(request)
        spots = Spot.objects.all()
        if request.query_params.get("scene_id"):
            spots = spots.filter(scene_id=request.query_params["scene_id"])
        spots = spots.annotate(
            event_count=Count(
                "checkin_events",
                filter=Q(checkin_events__id__in=events.values("id")),
            )
        ).order_by("-event_count", "name")
        return api_response(
            request,
            {
                "items": [
                    {"spot_id": str(s.id), "name": s.name, "event_count": s.event_count}
                    for s in spots
                ]
            },
        )


class LatestEventsView(CheckinListView):
    @extend_schema(operation_id="management_dashboard_latest_events")
    def get(self, request):
        return super().get(request)


class DeviceStatusView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        devices = Device.objects.all()
        if request.query_params.get("scene_id"):
            devices = devices.filter(scene_id=request.query_params["scene_id"])
        return api_response(
            request,
            {"items": [device_data(device) for device in devices]},
        )
