from django.urls import path

from .views import HeartbeatView

urlpatterns = [
    path("iot/heartbeat", HeartbeatView.as_view(), name="iot-heartbeat"),
]
