from rest_framework.response import Response


def api_response(request, data, status_code=200, meta=None):
    payload = {"data": data}
    if meta is not None:
        payload["meta"] = meta
    payload["request_id"] = request.request_id
    return Response(payload, status=status_code)
