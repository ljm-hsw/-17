import json

from django.core.serializers.json import DjangoJSONEncoder

from .models import AuditLog


def _json_safe(value):
    return json.loads(json.dumps(value, cls=DjangoJSONEncoder))


def record_audit(*, request, action, target, before, after, reason=""):
    return AuditLog.objects.create(
        actor=request.user,
        actor_role="system_admin" if request.user.is_superuser else "staff",
        action=action,
        target_type=target._meta.label_lower,
        target_id=str(target.pk),
        before=_json_safe(before),
        after=_json_safe(after),
        reason=reason,
        request_id=getattr(request, "request_id", ""),
    )
