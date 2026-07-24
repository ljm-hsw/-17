from django.urls import path

from .views import (
    CardCheckinListView,
    HomeView,
    PersonalCheckinListView,
    TodayVisitView,
    VisitDetailView,
    VisitHistoryView,
)

urlpatterns = [
    path("me/home", HomeView.as_view(), name="my-home"),
    path("me/visits/today", TodayVisitView.as_view(), name="today-visit"),
    path("me/visits/history", VisitHistoryView.as_view(), name="visit-history"),
    path("me/visits/<uuid:visit_id>", VisitDetailView.as_view(), name="visit-detail"),
    path("me/checkins", PersonalCheckinListView.as_view(), name="my-checkins"),
    path(
        "me/cards/<uuid:card_id>/checkins",
        CardCheckinListView.as_view(),
        name="card-checkins",
    ),
]
