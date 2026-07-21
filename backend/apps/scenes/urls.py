from django.urls import path

from .views import (
    RelatedSpotListView,
    RouteDetailView,
    SceneDetailView,
    SceneRouteListView,
    SceneSpotListView,
    SpotDetailView,
)

urlpatterns = [
    path("scenes/<slug:scene_slug>", SceneDetailView.as_view(), name="scene-detail"),
    path(
        "scenes/<slug:scene_slug>/spots",
        SceneSpotListView.as_view(),
        name="scene-spot-list",
    ),
    path(
        "scenes/<slug:scene_slug>/routes",
        SceneRouteListView.as_view(),
        name="scene-route-list",
    ),
    path("spots/<uuid:spot_id>", SpotDetailView.as_view(), name="spot-detail"),
    path(
        "spots/<uuid:spot_id>/related",
        RelatedSpotListView.as_view(),
        name="related-spot-list",
    ),
    path("routes/<uuid:route_id>", RouteDetailView.as_view(), name="route-detail"),
]
