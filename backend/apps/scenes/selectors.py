from .models import PublishStatus, Route, Scene, Spot


def get_published_scene(slug):
    return Scene.objects.get(slug=slug, status=PublishStatus.PUBLISHED)


def list_published_spots(scene, category=None):
    queryset = scene.spots.filter(status=PublishStatus.PUBLISHED).prefetch_related("media")
    if category:
        queryset = queryset.filter(category=category)
    return queryset


def get_published_spot(spot_id):
    return (
        Spot.objects.select_related("scene")
        .prefetch_related("media")
        .get(
            id=spot_id,
            status=PublishStatus.PUBLISHED,
            scene__status=PublishStatus.PUBLISHED,
        )
    )


def list_published_routes(scene):
    return (
        Route.objects.filter(scene=scene, status=PublishStatus.PUBLISHED)
        .prefetch_related("route_spots__spot__media")
        .order_by("name")
    )


def get_published_route(route_id):
    return (
        Route.objects.filter(status=PublishStatus.PUBLISHED, scene__status=PublishStatus.PUBLISHED)
        .prefetch_related("route_spots__spot__media")
        .get(id=route_id)
    )
