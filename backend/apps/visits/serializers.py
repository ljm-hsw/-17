from rest_framework import serializers

from .models import CheckinEvent, VisitSession
from .selectors import get_checkin_progress, get_route_timeline


class CheckinEventSerializer(serializers.ModelSerializer):
    spot_id = serializers.UUIDField(read_only=True)
    spot_name = serializers.CharField(source="spot.name", read_only=True)
    card_id = serializers.UUIDField(read_only=True)
    card_serial_no = serializers.CharField(source="card.serial_no", read_only=True)

    class Meta:
        model = CheckinEvent
        fields = (
            "id",
            "event_id",
            "spot_id",
            "spot_name",
            "card_id",
            "card_serial_no",
            "checkin_type",
            "received_at",
            "device_time",
        )


class VisitSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = VisitSession
        fields = (
            "id",
            "scene_id",
            "local_date",
            "started_at",
            "last_checkin_at",
        )


def visit_summary_data(*, user, scene, session):
    progress = get_checkin_progress(user, session, scene)
    route = [
        {
            "event_id": event.event_id,
            "spot_id": str(event.spot_id),
            "spot_name": event.spot.name,
            "checked_in_at": event.received_at,
        }
        for event in get_route_timeline(user, session)
    ]
    return {
        "visit_id": str(session.id) if session else None,
        "scene_id": str(scene.id),
        "local_date": session.local_date if session else None,
        **progress,
        "route": route,
    }
