from django.urls import path

from .views import CheckinView, HeartbeatView

urlpatterns = [
    path("iot/heartbeat", HeartbeatView.as_view(), name="iot-heartbeat"),
    path("iot/checkins", CheckinView.as_view(), name="iot-checkins"),
]
