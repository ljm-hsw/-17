from dataclasses import dataclass
from zoneinfo import ZoneInfo

from django.db import IntegrityError, transaction
from django.utils import timezone

from apps.accounts.models import Card, CardBinding
from apps.accounts.uid import digest_card_uid

from .models import CheckinEvent, VisitSession


@dataclass(frozen=True)
class CheckinResult:
    data: dict
    duplicate: bool = False


def _event_result(event, *, duplicate=False):
    return CheckinResult(data=event.result_snapshot, duplicate=duplicate)


def _result_payload(*, event_id, status, spot, failure_code=""):
    data = {
        "event_id": event_id,
        "status": status,
        "feedback_code": (
            "EVENT_ACCEPTED" if status == CheckinEvent.Status.ACCEPTED else "EVENT_REJECTED"
        ),
        "spot": {"id": str(spot.id), "name": spot.name},
    }
    if failure_code:
        data["failure_code"] = failure_code
    return data


def _create_rejected_event(
    *,
    device,
    payload,
    failure_code,
    card_uid_hmac="",
    card=None,
    binding=None,
):
    event = CheckinEvent.objects.create(
        event_id=payload["event_id"],
        device=device,
        spot=device.spot,
        user=binding.user if binding else None,
        card=card,
        card_binding=binding,
        card_uid_hmac=card_uid_hmac,
        checkin_type=payload["checkin_type"],
        status=CheckinEvent.Status.REJECTED,
        failure_code=failure_code,
        device_time=payload.get("device_time"),
    )
    event.result_snapshot = _result_payload(
        event_id=event.event_id,
        status=event.status,
        spot=event.spot,
        failure_code=failure_code,
    )
    event.save(update_fields=("result_snapshot",))
    return _event_result(event)


def _process_checkin(*, device, payload):
    existing = (
        CheckinEvent.objects.select_for_update()
        .filter(device=device, event_id=payload["event_id"])
        .first()
    )
    if existing:
        return _event_result(existing, duplicate=True)

    if payload["spot_id"] != device.spot_id:
        return _create_rejected_event(
            device=device,
            payload=payload,
            failure_code="SPOT_MISMATCH",
        )

    uid_hmac = digest_card_uid(payload["card_uid"])
    card = Card.objects.filter(uid_hmac=uid_hmac).first()
    if card is None:
        return _create_rejected_event(
            device=device,
            payload=payload,
            failure_code="CARD_UNREGISTERED",
            card_uid_hmac=uid_hmac,
        )

    binding = (
        CardBinding.objects.select_related("user")
        .filter(card=card, unbound_at__isnull=True)
        .first()
    )
    if card.status in {Card.Status.LOST, Card.Status.DISABLED}:
        return _create_rejected_event(
            device=device,
            payload=payload,
            failure_code="CARD_DISABLED",
            card_uid_hmac=uid_hmac,
            card=card,
            binding=binding,
        )
    if binding is None:
        return _create_rejected_event(
            device=device,
            payload=payload,
            failure_code="CARD_UNBOUND",
            card_uid_hmac=uid_hmac,
            card=card,
        )
    if card.status != Card.Status.ACTIVE:
        return _create_rejected_event(
            device=device,
            payload=payload,
            failure_code="CARD_DISABLED",
            card_uid_hmac=uid_hmac,
            card=card,
            binding=binding,
        )

    now = timezone.now()
    local_date = now.astimezone(ZoneInfo(device.scene.timezone)).date()
    session, _ = VisitSession.objects.get_or_create(
        user=binding.user,
        scene=device.scene,
        local_date=local_date,
        defaults={"started_at": now, "last_checkin_at": now},
    )
    event = CheckinEvent.objects.create(
        event_id=payload["event_id"],
        device=device,
        spot=device.spot,
        user=binding.user,
        card=card,
        card_binding=binding,
        visit_session=session,
        card_uid_hmac=uid_hmac,
        checkin_type=payload["checkin_type"],
        status=CheckinEvent.Status.ACCEPTED,
        device_time=payload.get("device_time"),
    )
    session.last_checkin_at = now
    session.save(update_fields=("last_checkin_at", "updated_at"))
    card.last_used_at = now
    card.save(update_fields=("last_used_at", "updated_at"))
    event.result_snapshot = _result_payload(
        event_id=event.event_id,
        status=event.status,
        spot=event.spot,
    )
    event.save(update_fields=("result_snapshot",))
    return _event_result(event)


def process_checkin(*, device, payload):
    for attempt in range(2):
        try:
            with transaction.atomic():
                return _process_checkin(device=device, payload=payload)
        except IntegrityError:
            event = CheckinEvent.objects.filter(
                device=device,
                event_id=payload["event_id"],
            ).first()
            if event:
                return _event_result(event, duplicate=True)
            if attempt:
                raise
    raise RuntimeError("unreachable")
