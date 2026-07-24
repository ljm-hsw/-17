import uuid

from django.db import models


class VisitSession(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        "accounts.User",
        on_delete=models.PROTECT,
        related_name="visit_sessions",
    )
    scene = models.ForeignKey(
        "scenes.Scene",
        on_delete=models.PROTECT,
        related_name="visit_sessions",
    )
    local_date = models.DateField()
    started_at = models.DateTimeField()
    last_checkin_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-local_date", "-started_at")
        constraints = (
            models.UniqueConstraint(
                fields=("user", "scene", "local_date"),
                name="uniq_daily_visit_per_user_scene",
            ),
        )


class CheckinEvent(models.Model):
    class CheckinType(models.TextChoices):
        NFC = "nfc", "NFC"
        RFID = "rfid", "RFID"
        MANUAL_ADMIN = "manual_admin", "管理员补录"

    class Status(models.TextChoices):
        ACCEPTED = "accepted", "已接受"
        REJECTED = "rejected", "已拒绝"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    event_id = models.CharField(max_length=128)
    device = models.ForeignKey(
        "iot.Device",
        on_delete=models.PROTECT,
        related_name="checkin_events",
    )
    spot = models.ForeignKey(
        "scenes.Spot",
        on_delete=models.PROTECT,
        related_name="checkin_events",
    )
    user = models.ForeignKey(
        "accounts.User",
        on_delete=models.PROTECT,
        related_name="checkin_events",
        null=True,
        blank=True,
    )
    card = models.ForeignKey(
        "accounts.Card",
        on_delete=models.PROTECT,
        related_name="checkin_events",
        null=True,
        blank=True,
    )
    card_binding = models.ForeignKey(
        "accounts.CardBinding",
        on_delete=models.PROTECT,
        related_name="checkin_events",
        null=True,
        blank=True,
    )
    visit_session = models.ForeignKey(
        VisitSession,
        on_delete=models.PROTECT,
        related_name="checkin_events",
        null=True,
        blank=True,
    )
    card_uid_hmac = models.CharField(max_length=64, blank=True)
    checkin_type = models.CharField(max_length=16, choices=CheckinType.choices)
    status = models.CharField(max_length=16, choices=Status.choices, db_index=True)
    failure_code = models.CharField(max_length=64, blank=True)
    device_time = models.DateTimeField(null=True, blank=True)
    received_at = models.DateTimeField(auto_now_add=True)
    result_snapshot = models.JSONField(default=dict)

    class Meta:
        ordering = ("received_at", "id")
        constraints = (
            models.UniqueConstraint(
                fields=("device", "event_id"),
                name="uniq_event_id_per_device",
            ),
        )
        indexes = (
            models.Index(fields=("user", "received_at"), name="checkin_user_received_idx"),
            models.Index(fields=("card", "received_at"), name="checkin_card_received_idx"),
            models.Index(fields=("spot", "received_at"), name="checkin_spot_received_idx"),
            models.Index(fields=("device", "received_at"), name="checkin_device_received_idx"),
            models.Index(
                fields=("visit_session", "status", "received_at"),
                name="checkin_session_status_idx",
            ),
        )
