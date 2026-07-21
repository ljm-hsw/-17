from django.urls import path
from rest_framework.permissions import IsAdminUser
from rest_framework.views import APIView

from apps.accounts.management_views import (
    ActivationCodeCreateView,
    CardBindingListView,
    CardDetailView,
    CardImportConfirmView,
    CardImportPreviewView,
    CardListView,
    ForceUnbindView,
    UserCardListView,
    UserDetailView,
    UserListView,
)
from apps.iot.management_views import (
    DeviceDetailView,
    DeviceListView,
    DeviceRotateSecretView,
)
from apps.scenes.management_views import (
    RouteDetailView,
    RouteListView,
    SceneDetailView,
    SceneListView,
    SpotDetailView,
    SpotDisableView,
    SpotListView,
    SpotMediaCreateView,
    SpotMediaDetailView,
    SpotMediaDisableView,
    SpotPublishView,
    SpotStatisticsView,
)
from apps.visits.management_views import (
    CardCheckinListView,
    CheckinDetailView,
    CheckinListView,
    CheckinTrendView,
    DashboardSummaryView,
    DeviceCheckinListView,
    DeviceStatusView,
    LatestEventsView,
    SpotCheckinListView,
    SpotRankingView,
    UserCheckinListView,
    UserVisitListView,
    VisitDetailView,
    VisitListView,
)

from .management import audit_data, list_response
from .models import AuditLog


class AuditLogListView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        return list_response(request, AuditLog.objects.select_related("actor"), audit_data)

urlpatterns = [
    path("dashboard/summary", DashboardSummaryView.as_view()),
    path("dashboard/checkin-trend", CheckinTrendView.as_view()),
    path("dashboard/spot-ranking", SpotRankingView.as_view()),
    path("dashboard/latest-events", LatestEventsView.as_view()),
    path("dashboard/device-status", DeviceStatusView.as_view()),
    path("users", UserListView.as_view()),
    path("users/<uuid:user_id>", UserDetailView.as_view()),
    path("users/<uuid:user_id>/cards", UserCardListView.as_view()),
    path("users/<uuid:user_id>/visits", UserVisitListView.as_view()),
    path(
        "users/<uuid:object_id>/checkins",
        UserCheckinListView.as_view(),
    ),
    path("scenes", SceneListView.as_view()),
    path("scenes/<uuid:scene_id>", SceneDetailView.as_view()),
    path("spots", SpotListView.as_view()),
    path("spots/<uuid:spot_id>", SpotDetailView.as_view()),
    path("spots/<uuid:spot_id>/publish", SpotPublishView.as_view()),
    path("spots/<uuid:spot_id>/disable", SpotDisableView.as_view()),
    path("spots/<uuid:spot_id>/media", SpotMediaCreateView.as_view()),
    path(
        "spots/<uuid:spot_id>/media/<uuid:media_id>",
        SpotMediaDetailView.as_view(),
    ),
    path(
        "spots/<uuid:spot_id>/media/<uuid:media_id>/disable",
        SpotMediaDisableView.as_view(),
    ),
    path("spots/<uuid:spot_id>/statistics", SpotStatisticsView.as_view()),
    path("spots/<uuid:object_id>/checkins", SpotCheckinListView.as_view()),
    path("cards", CardListView.as_view()),
    path("cards/import-preview", CardImportPreviewView.as_view()),
    path("cards/import-confirm", CardImportConfirmView.as_view()),
    path("cards/<uuid:card_id>", CardDetailView.as_view()),
    path(
        "cards/<uuid:card_id>/activation-codes",
        ActivationCodeCreateView.as_view(),
    ),
    path("cards/<uuid:card_id>/bindings", CardBindingListView.as_view()),
    path("cards/<uuid:object_id>/checkins", CardCheckinListView.as_view()),
    path("devices", DeviceListView.as_view()),
    path("devices/<uuid:device_id>", DeviceDetailView.as_view()),
    path(
        "devices/<uuid:device_id>/rotate-secret",
        DeviceRotateSecretView.as_view(),
    ),
    path("devices/<uuid:object_id>/checkins", DeviceCheckinListView.as_view()),
    path("routes", RouteListView.as_view()),
    path("routes/<uuid:route_id>", RouteDetailView.as_view()),
    path("visits", VisitListView.as_view()),
    path("visits/<uuid:visit_id>", VisitDetailView.as_view()),
    path("checkins", CheckinListView.as_view()),
    path("checkins/<uuid:event_id>", CheckinDetailView.as_view()),
    path(
        "bindings/<uuid:binding_id>/force-unbind",
        ForceUnbindView.as_view(),
    ),
    path("audit-logs", AuditLogListView.as_view()),
]
