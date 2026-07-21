from django.db import transaction
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAdminUser

from apps.common.api import api_response
from apps.common.audit import record_audit
from apps.common.management import list_response, require_confirmed_reason
from apps.common.permissions import HasManagementModelPermission
from apps.common.schema import SchemaAPIView as APIView
from apps.visits.models import CheckinEvent

from .models import PublishStatus, Route, RouteSpot, Scene, Spot, SpotMedia


def scene_data(scene):
    return {
        "id": str(scene.id),
        "slug": scene.slug,
        "name": scene.name,
        "subtitle": scene.subtitle,
        "timezone": scene.timezone,
        "map_image_url": scene.map_image_url,
        "status": scene.status,
    }


def spot_data(spot):
    return {
        "id": str(spot.id),
        "scene_id": str(spot.scene_id),
        "slug": spot.slug,
        "name": spot.name,
        "category": spot.category,
        "summary": spot.summary,
        "description": spot.description,
        "knowledge_content": spot.knowledge_content,
        "map_x": str(spot.map_x),
        "map_y": str(spot.map_y),
        "tags": spot.tags,
        "suggested_stay_minutes": spot.suggested_stay_minutes,
        "status": spot.status,
        "is_checkin_enabled": spot.is_checkin_enabled,
        "is_photo_spot": spot.is_photo_spot,
        "media": [media_data(item) for item in spot.media.order_by("sort_order", "id")],
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


def media_data(media):
    return {
        "id": str(media.id),
        "spot_id": str(media.spot_id),
        "url": media.url,
        "storage_key": media.storage_key,
        "media_type": media.media_type,
        "caption": media.caption,
        "sort_order": media.sort_order,
        "status": media.status,
    }


class SceneListView(APIView):
    permission_classes = [HasManagementModelPermission]
    management_model = Scene

    @extend_schema(operation_id="management_scenes_list")
    def get(self, request):
        return list_response(request, Scene.objects.order_by("name"), scene_data)

    @transaction.atomic
    def post(self, request):
        scene = Scene.objects.create(
            slug=request.data.get("slug", ""),
            name=request.data.get("name", ""),
            subtitle=request.data.get("subtitle", ""),
            timezone=request.data.get("timezone", "Asia/Shanghai"),
            map_image_url=request.data.get("map_image_url", ""),
            status=request.data.get("status", PublishStatus.DRAFT),
        )
        record_audit(
            request=request,
            action="scene.create",
            target=scene,
            before={},
            after=scene_data(scene),
        )
        return api_response(request, scene_data(scene), status_code=201)


class SceneDetailView(APIView):
    permission_classes = [HasManagementModelPermission]
    management_model = Scene

    @extend_schema(operation_id="management_scenes_retrieve")
    def get(self, request, scene_id):
        return api_response(request, scene_data(get_object_or_404(Scene, id=scene_id)))

    @transaction.atomic
    def patch(self, request, scene_id):
        scene = get_object_or_404(Scene, id=scene_id)
        before = scene_data(scene)
        for field in ("slug", "name", "subtitle", "timezone", "map_image_url", "status"):
            if field in request.data:
                setattr(scene, field, request.data[field])
        scene.save()
        record_audit(
            request=request,
            action="scene.update",
            target=scene,
            before=before,
            after=scene_data(scene),
        )
        return api_response(request, scene_data(scene))


class SpotListView(APIView):
    permission_classes = [HasManagementModelPermission]
    management_model = Spot

    @extend_schema(operation_id="management_spots_list")
    def get(self, request):
        spots = Spot.objects.select_related("scene").prefetch_related("media")
        if request.query_params.get("scene_id"):
            spots = spots.filter(scene_id=request.query_params["scene_id"])
        if request.query_params.get("status"):
            spots = spots.filter(status=request.query_params["status"])
        search = request.query_params.get("search")
        if search:
            spots = spots.filter(Q(name__icontains=search) | Q(slug__icontains=search))
        return list_response(request, spots, spot_data)

    @transaction.atomic
    def post(self, request):
        scene = get_object_or_404(Scene, id=request.data.get("scene_id"))
        spot = Spot.objects.create(
            scene=scene,
            slug=request.data.get("slug", ""),
            name=request.data.get("name", ""),
            category=request.data.get("category", "checkin"),
            summary=request.data.get("summary", ""),
            description=request.data.get("description", ""),
            knowledge_content=request.data.get("knowledge_content", ""),
            map_x=request.data.get("map_x", 0),
            map_y=request.data.get("map_y", 0),
            tags=request.data.get("tags", []),
            suggested_stay_minutes=request.data.get("suggested_stay_minutes", 15),
            is_checkin_enabled=request.data.get("is_checkin_enabled", True),
            is_photo_spot=request.data.get("is_photo_spot", False),
            status=request.data.get("status", PublishStatus.DRAFT),
        )
        record_audit(
            request=request,
            action="spot.create",
            target=spot,
            before={},
            after=spot_data(spot),
        )
        return api_response(request, spot_data(spot), status_code=201)


class SpotDetailView(APIView):
    permission_classes = [HasManagementModelPermission]
    management_model = Spot

    @extend_schema(operation_id="management_spots_retrieve")
    def get(self, request, spot_id):
        spot = get_object_or_404(Spot.objects.prefetch_related("media"), id=spot_id)
        return api_response(request, spot_data(spot))

    @transaction.atomic
    def patch(self, request, spot_id):
        spot = get_object_or_404(Spot, id=spot_id)
        before = spot_data(spot)
        fields = (
            "slug",
            "name",
            "category",
            "summary",
            "description",
            "knowledge_content",
            "map_x",
            "map_y",
            "tags",
            "suggested_stay_minutes",
            "is_checkin_enabled",
            "is_photo_spot",
            "status",
        )
        for field in fields:
            if field in request.data:
                setattr(spot, field, request.data[field])
        spot.save()
        record_audit(
            request=request,
            action="spot.update",
            target=spot,
            before=before,
            after=spot_data(spot),
        )
        return api_response(request, spot_data(spot))


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
    permission_classes = [HasManagementModelPermission]
    management_model = Route

    @extend_schema(operation_id="management_routes_list")
    def get(self, request):
        routes = Route.objects.prefetch_related("route_spots")
        if request.query_params.get("scene_id"):
            routes = routes.filter(scene_id=request.query_params["scene_id"])
        if request.query_params.get("status"):
            routes = routes.filter(status=request.query_params["status"])
        search = request.query_params.get("search")
        if search:
            routes = routes.filter(Q(name__icontains=search) | Q(slug__icontains=search))
        return list_response(request, routes, route_data)

    @transaction.atomic
    def post(self, request):
        scene = get_object_or_404(Scene, id=request.data.get("scene_id"))
        stops = _validated_stops(scene, request.data.get("stops", []))
        route = Route.objects.create(
            scene=scene,
            slug=request.data.get("slug", ""),
            name=request.data.get("name", ""),
            summary=request.data.get("summary", ""),
            estimated_minutes=request.data.get("estimated_minutes", 0),
            status=request.data.get("status", PublishStatus.DRAFT),
        )
        _replace_stops(route, stops)
        record_audit(
            request=request,
            action="route.create",
            target=route,
            before={},
            after=route_data(route),
        )
        return api_response(request, route_data(route), status_code=201)


class RouteDetailView(APIView):
    permission_classes = [HasManagementModelPermission]
    management_model = Route

    @extend_schema(operation_id="management_routes_retrieve")
    def get(self, request, route_id):
        route = get_object_or_404(Route.objects.prefetch_related("route_spots"), id=route_id)
        return api_response(request, route_data(route))

    @transaction.atomic
    def patch(self, request, route_id):
        route = get_object_or_404(Route.objects.prefetch_related("route_spots"), id=route_id)
        before = route_data(route)
        for field in ("slug", "name", "summary", "estimated_minutes", "status"):
            if field in request.data:
                setattr(route, field, request.data[field])
        route.save()
        if "stops" in request.data:
            _replace_stops(route, _validated_stops(route.scene, request.data["stops"]))
        record_audit(
            request=request,
            action="route.update",
            target=route,
            before=before,
            after=route_data(route),
        )
        return api_response(request, route_data(route))


def _validated_stops(scene, rows):
    if not isinstance(rows, list):
        raise ValidationError({"stops": "路线点位必须是数组"})
    spot_ids = [row.get("spot_id") for row in rows]
    orders = [row.get("order") for row in rows]
    if len(spot_ids) != len(set(spot_ids)) or len(orders) != len(set(orders)):
        raise ValidationError({"stops": "点位和顺序不得重复"})
    spots = {str(item.id): item for item in Spot.objects.filter(id__in=spot_ids, scene=scene)}
    if len(spots) != len(spot_ids):
        raise ValidationError({"stops": "路线中的点位必须属于同一场景"})
    return [(spots[str(row["spot_id"])], row["order"], row.get("note", "")) for row in rows]


def _replace_stops(route, stops):
    route.route_spots.all().delete()
    RouteSpot.objects.bulk_create(
        [RouteSpot(route=route, spot=spot, order=order, note=note) for spot, order, note in stops]
    )
    getattr(route, "_prefetched_objects_cache", {}).pop("route_spots", None)


class SpotPublishView(APIView):
    permission_classes = [HasManagementModelPermission]
    management_model = Spot
    permission_action = "change"

    @transaction.atomic
    def post(self, request, spot_id):
        spot = get_object_or_404(Spot, id=spot_id)
        before = spot_data(spot)
        spot.status = PublishStatus.PUBLISHED
        spot.save(update_fields=("status", "updated_at"))
        record_audit(
            request=request,
            action="spot.publish",
            target=spot,
            before=before,
            after=spot_data(spot),
        )
        return api_response(request, spot_data(spot))


class SpotDisableView(APIView):
    permission_classes = [HasManagementModelPermission]
    management_model = Spot
    permission_action = "change"

    @transaction.atomic
    def post(self, request, spot_id):
        reason = require_confirmed_reason(request.data)
        spot = get_object_or_404(Spot, id=spot_id)
        before = spot_data(spot)
        spot.status = PublishStatus.DISABLED
        spot.save(update_fields=("status", "updated_at"))
        record_audit(
            request=request,
            action="spot.disable",
            target=spot,
            before=before,
            after=spot_data(spot),
            reason=reason,
        )
        return api_response(request, spot_data(spot))


class SpotMediaCreateView(APIView):
    permission_classes = [HasManagementModelPermission]
    management_model = SpotMedia
    permission_action = "add"

    @transaction.atomic
    def post(self, request, spot_id):
        spot = get_object_or_404(Spot, id=spot_id)
        media = SpotMedia.objects.create(
            spot=spot,
            url=request.data.get("url", ""),
            storage_key=request.data.get("storage_key", ""),
            media_type=request.data.get("media_type", SpotMedia.MediaType.IMAGE),
            caption=request.data.get("caption", ""),
            sort_order=request.data.get("sort_order", 0),
            status=request.data.get("status", PublishStatus.DRAFT),
        )
        record_audit(
            request=request,
            action="spot_media.create",
            target=media,
            before={},
            after=media_data(media),
        )
        return api_response(request, media_data(media), status_code=201)


class SpotMediaDetailView(APIView):
    permission_classes = [HasManagementModelPermission]
    management_model = SpotMedia
    permission_action = "change"

    @transaction.atomic
    def patch(self, request, spot_id, media_id):
        media = get_object_or_404(SpotMedia, id=media_id, spot_id=spot_id)
        before = media_data(media)
        for field in ("url", "storage_key", "media_type", "caption", "sort_order", "status"):
            if field in request.data:
                setattr(media, field, request.data[field])
        media.save()
        record_audit(
            request=request,
            action="spot_media.update",
            target=media,
            before=before,
            after=media_data(media),
        )
        return api_response(request, media_data(media))


class SpotMediaDisableView(APIView):
    permission_classes = [HasManagementModelPermission]
    management_model = SpotMedia
    permission_action = "change"

    @transaction.atomic
    def post(self, request, spot_id, media_id):
        reason = require_confirmed_reason(request.data)
        media = get_object_or_404(SpotMedia, id=media_id, spot_id=spot_id)
        before = media_data(media)
        media.status = PublishStatus.DISABLED
        media.save(update_fields=("status", "updated_at"))
        record_audit(
            request=request,
            action="spot_media.disable",
            target=media,
            before=before,
            after=media_data(media),
            reason=reason,
        )
        return api_response(request, media_data(media))
