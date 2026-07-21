from django.http import Http404
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from apps.accounts.models import Card
from apps.accounts.selectors import list_user_bindings
from apps.accounts.serializers import CardBindingSerializer
from apps.common.api import api_response
from apps.scenes.models import Scene
from apps.scenes.selectors import get_published_scene
from apps.scenes.serializers import SceneSerializer, SpotSerializer

from .models import VisitSession
from .selectors import (
    accepted_events_for_user,
    get_current_visit,
    list_unvisited_spots,
    list_user_checkins,
)
from .serializers import CheckinEventSerializer, VisitSessionSerializer, visit_summary_data


def _scene_or_404(slug):
    try:
        return get_published_scene(slug)
    except Scene.DoesNotExist as exc:
        raise Http404 from exc


def _pagination(request, queryset):
    try:
        page = max(1, int(request.query_params.get("page", 1)))
        page_size = min(100, max(1, int(request.query_params.get("page_size", 20))))
    except ValueError:
        page, page_size = 1, 20
    total = queryset.count()
    start = (page - 1) * page_size
    return queryset[start : start + page_size], {
        "page": page,
        "page_size": page_size,
        "total": total,
    }


class TodayVisitView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        scene = _scene_or_404(request.query_params.get("scene", ""))
        session = get_current_visit(request.user, scene)
        return api_response(
            request,
            visit_summary_data(user=request.user, scene=scene, session=session),
        )


class VisitHistoryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        sessions = VisitSession.objects.filter(user=request.user).select_related("scene")
        page, meta = _pagination(request, sessions)
        return api_response(
            request,
            {"items": VisitSessionSerializer(page, many=True).data},
            meta=meta,
        )


class VisitDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, visit_id):
        session = get_object_or_404(
            VisitSession.objects.select_related("scene"),
            id=visit_id,
            user=request.user,
        )
        return api_response(
            request,
            visit_summary_data(user=request.user, scene=session.scene, session=session),
        )


class PersonalCheckinListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        events = list_user_checkins(
            request.user,
            {
                "card_id": request.query_params.get("card_id"),
                "spot_id": request.query_params.get("spot_id"),
                "date": request.query_params.get("date"),
            },
        )
        page, meta = _pagination(request, events)
        return api_response(
            request,
            {"items": CheckinEventSerializer(page, many=True).data},
            meta=meta,
        )


class CardCheckinListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, card_id):
        card = get_object_or_404(
            Card.objects.filter(bindings__user=request.user).distinct(),
            id=card_id,
        )
        events = list_user_checkins(request.user, {"card_id": str(card.id)})
        page, meta = _pagination(request, events)
        return api_response(
            request,
            {"items": CheckinEventSerializer(page, many=True).data},
            meta=meta,
        )


class HomeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        scene = _scene_or_404(request.query_params.get("scene", ""))
        session = get_current_visit(request.user, scene)
        bindings = list_user_bindings(request.user)
        primary = bindings.filter(is_primary=True).first()
        latest = accepted_events_for_user(request.user).filter(spot__scene=scene).last()
        recommendations = list_unvisited_spots(request.user, scene)[:4]
        return api_response(
            request,
            {
                "scene": SceneSerializer(scene).data,
                "primary_card": CardBindingSerializer(primary).data if primary else None,
                "active_card_count": bindings.count(),
                "visit": visit_summary_data(
                    user=request.user,
                    scene=scene,
                    session=session,
                ),
                "latest_checkin": CheckinEventSerializer(latest).data if latest else None,
                "recommended_spots": SpotSerializer(
                    recommendations,
                    many=True,
                    context={"request": request},
                ).data,
            },
        )
