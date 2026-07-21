from apps.common.api import api_response


def boolean_query_param(request, name):
    from rest_framework.exceptions import ValidationError

    value = request.query_params.get(name)
    if value is None:
        return None
    normalized = value.strip().lower()
    if normalized == "true":
        return True
    if normalized == "false":
        return False
    raise ValidationError({name: "必须为 true 或 false"})


def require_confirmed_reason(data):
    from rest_framework.exceptions import ValidationError

    reason = str(data.get("reason", "")).strip()
    if data.get("confirm") is not True or not reason:
        raise ValidationError({"confirm": "必须确认操作", "reason": "必须填写操作原因"})
    return reason


def paginate(request, queryset):
    try:
        page = max(1, int(request.query_params.get("page", 1)))
        page_size = min(100, max(1, int(request.query_params.get("page_size", 20))))
    except ValueError:
        page, page_size = 1, 20
    total = queryset.count()
    start = (page - 1) * page_size
    return queryset[start : start + page_size], {
        "page": page,
        "page_size": page_size,
        "total": total,
    }


def list_response(request, queryset, serializer):
    page, meta = paginate(request, queryset)
    return api_response(request, {"items": [serializer(item) for item in page]}, meta=meta)


def audit_data(log):
    return {
        "id": str(log.id),
        "actor_id": str(log.actor_id),
        "actor_username": log.actor.username,
        "actor_role": log.actor_role,
        "action": log.action,
        "target_type": log.target_type,
        "target_id": log.target_id,
        "before": log.before,
        "after": log.after,
        "reason": log.reason,
        "request_id": log.request_id,
        "created_at": log.created_at,
    }
