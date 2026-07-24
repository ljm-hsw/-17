from datetime import date
from zoneinfo import ZoneInfo

from django.utils import timezone

from apps.scenes.models import PublishStatus, Spot

from .models import CheckinEvent, VisitSession


def accepted_events_for_user(user):
    return (
        CheckinEvent.objects.filter(user=user, status=CheckinEvent.Status.ACCEPTED)
        .select_related("card", "spot", "device", "visit_session")
        .order_by("received_at", "id")
    )


def scene_local_date(scene):
    return timezone.now().astimezone(ZoneInfo(scene.timezone)).date()


def get_current_visit(user, scene, on_date=None):
    local_date = on_date or scene_local_date(scene)
    return VisitSession.objects.filter(
        user=user,
        scene=scene,
        local_date=local_date,
    ).first()


def get_route_timeline(user, session):
    if session is None:
        return []
    events = accepted_events_for_user(user).filter(visit_session=session)
    seen_spots = set()
    route = []
    for event in events:
        if event.spot_id in seen_spots:
            continue
        seen_spots.add(event.spot_id)
        route.append(event)
    return route


def get_checkin_progress(user, session, scene=None):
    scene = scene or session.scene
    total = Spot.objects.filter(
        scene=scene,
        status=PublishStatus.PUBLISHED,
        is_checkin_enabled=True,
    ).count()
    if session is None:
        return {"checked_spot_count": 0, "event_count": 0, "total_spot_count": total}
    events = accepted_events_for_user(user).filter(visit_session=session)
    return {
        "checked_spot_count": events.values("spot_id").distinct().count(),
        "event_count": events.count(),
        "total_spot_count": total,
    }


def list_user_checkins(user, filters=None):
    filters = filters or {}
    events = accepted_events_for_user(user)
    if filters.get("card_id"):
        events = events.filter(card_id=filters["card_id"])
    if filters.get("spot_id"):
        events = events.filter(spot_id=filters["spot_id"])
    if filters.get("date"):
        filter_date = date.fromisoformat(filters["date"])
        events = events.filter(visit_session__local_date=filter_date)
    return events


def list_unvisited_spots(user, scene):
    visited = accepted_events_for_user(user).filter(spot__scene=scene).values("spot_id")
    return Spot.objects.filter(
        scene=scene,
        status=PublishStatus.PUBLISHED,
        is_checkin_enabled=True,
    ).exclude(id__in=visited)
