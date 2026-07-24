from django.urls import path

from .views import (
    CardBindingDetailView,
    CardBindingListCreateView,
    DevLoginView,
    MeView,
    RefreshView,
    SetPrimaryCardView,
    WechatLoginView,
)

urlpatterns = [
    path("auth/wechat/login", WechatLoginView.as_view(), name="wechat-login"),
    path("auth/dev-login", DevLoginView.as_view(), name="dev-login"),
    path("auth/refresh", RefreshView.as_view(), name="token-refresh"),
    path("me", MeView.as_view(), name="me"),
    path("me/cards", CardBindingListCreateView.as_view(), name="my-card-list"),
    path("me/cards/bind", CardBindingListCreateView.as_view(), name="bind-card"),
    path(
        "me/cards/<uuid:binding_id>",
        CardBindingDetailView.as_view(),
        name="card-binding-detail",
    ),
    path(
        "me/cards/<uuid:binding_id>/set-primary",
        SetPrimaryCardView.as_view(),
        name="set-primary-card",
    ),
]
