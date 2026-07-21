from apps.common.api import api_response


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
