from django.db.models import Count
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAdminUser
from rest_framework.views import APIView

from apps.common.api import api_response
from apps.common.management import list_response
from apps.visits.models import CheckinEvent

from .models import Route, Scene, Spot


def scene_data(scene):
    return {
        "id": str(scene.id),
        "slug": scene.slug,
        "name": scene.name,
        "subtitle": scene.subtitle,
        "timezone": scene.timezone,
        "status": scene.status,
    }


def spot_data(spot):
    return {
        "id": str(spot.id),
        "scene_id": str(spot.scene_id),
        "slug": spot.slug,
        "name": spot.name,
        "category": spot.category,
        "status": spot.status,
        "is_checkin_enabled": spot.is_checkin_enabled,
    }


def route_data(route):
    return {
        "id": str(route.id),
        "scene_id": str(route.scene_id),
        "slug": route.slug,
        "name": route.name,
        "estimated_minutes": route.estimated_minutes,
        "status": route.status,
        "stops": [
            {"spot_id": str(stop.spot_id), "order": stop.order, "note": stop.note}
            for stop in route.route_spots.all()
        ],
    }


class SceneListView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        return list_response(request, Scene.objects.order_by("name"), scene_data)


class SceneDetailView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request, scene_id):
        return api_response(request, scene_data(get_object_or_404(Scene, id=scene_id)))


class SpotListView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        spots = Spot.objects.select_related("scene")
        if request.query_params.get("scene_id"):
            spots = spots.filter(scene_id=request.query_params["scene_id"])
        return list_response(request, spots, spot_data)


class SpotDetailView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request, spot_id):
        return api_response(request, spot_data(get_object_or_404(Spot, id=spot_id)))


class SpotStatisticsView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request, spot_id):
        spot = get_object_or_404(Spot, id=spot_id)
        aggregate = CheckinEvent.objects.filter(
            spot=spot,
            status=CheckinEvent.Status.ACCEPTED,
        ).aggregate(
            visitor_count=Count("user_id", distinct=True),
            event_count=Count("id"),
        )
        return api_response(request, {"spot_id": str(spot.id), **aggregate})


class RouteListView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        routes = Route.objects.prefetch_related("route_spots")
        if request.query_params.get("scene_id"):
            routes = routes.filter(scene_id=request.query_params["scene_id"])
        return list_response(request, routes, route_data)


class RouteDetailView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request, route_id):
        route = get_object_or_404(Route.objects.prefetch_related("route_spots"), id=route_id)
        return api_response(request, route_data(route))
