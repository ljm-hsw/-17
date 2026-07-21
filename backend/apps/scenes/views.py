from django.http import Http404
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView

from apps.common.api import api_response

from .models import Route, Scene, Spot
from .selectors import (
    get_published_route,
    get_published_scene,
    get_published_spot,
    list_published_routes,
    list_published_spots,
)
from .serializers import RouteSerializer, SceneSerializer, SpotSerializer


class SceneDetailView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, scene_slug):
        try:
            scene = get_published_scene(scene_slug)
        except Scene.DoesNotExist as exc:
            raise Http404 from exc
        return api_response(request, SceneSerializer(scene).data)


class SceneSpotListView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, scene_slug):
        try:
            scene = get_published_scene(scene_slug)
        except Scene.DoesNotExist as exc:
            raise Http404 from exc
        spots = list_published_spots(scene, request.query_params.get("category"))
        return api_response(
            request,
            {"items": SpotSerializer(spots, many=True, context={"request": request}).data},
        )


class SpotDetailView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, spot_id):
        try:
            spot = get_published_spot(spot_id)
        except Spot.DoesNotExist as exc:
            raise Http404 from exc
        return api_response(
            request,
            SpotSerializer(spot, context={"request": request}).data,
        )


class RelatedSpotListView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, spot_id):
        try:
            spot = get_published_spot(spot_id)
        except Spot.DoesNotExist as exc:
            raise Http404 from exc
        related = list_published_spots(spot.scene, spot.category).exclude(id=spot.id)[:4]
        return api_response(
            request,
            {"items": SpotSerializer(related, many=True, context={"request": request}).data},
        )


class SceneRouteListView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, scene_slug):
        try:
            scene = get_published_scene(scene_slug)
        except Scene.DoesNotExist as exc:
            raise Http404 from exc
        routes = list_published_routes(scene)
        return api_response(request, {"items": RouteSerializer(routes, many=True).data})


class RouteDetailView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, route_id):
        try:
            route = get_published_route(route_id)
        except Route.DoesNotExist as exc:
            raise Http404 from exc
        return api_response(request, RouteSerializer(route).data)
