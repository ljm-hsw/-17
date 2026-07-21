from django.http import JsonResponse
from rest_framework.exceptions import APIException
from rest_framework.views import exception_handler

STATUS_ERROR_CODES = {
    400: "VALIDATION_ERROR",
    401: "AUTH_REQUIRED",
    403: "PERMISSION_DENIED",
    404: "RESOURCE_NOT_FOUND",
    409: "CONFLICT",
    429: "RATE_LIMITED",
}

STATUS_ERROR_MESSAGES = {
    400: "请求参数不正确",
    401: "请先登录",
    403: "没有权限执行此操作",
    404: "请求的资源不存在",
    409: "当前操作与资源状态冲突",
    429: "请求过于频繁，请稍后再试",
}


class ApiError(APIException):
    def __init__(self, code, message, status_code, details=None):
        self.status_code = status_code
        self.code = code
        self.message = message
        self.details = details or {}
        super().__init__(detail=message, code=code)


def _request_id(request):
    return getattr(request, "request_id", "")


def _error_payload(*, code, message, details, request):
    return {
        "error": {"code": code, "message": message, "details": details},
        "request_id": _request_id(request),
    }


def api_exception_handler(exc, context):
    request = context["request"]
    if isinstance(exc, ApiError):
        from rest_framework.response import Response

        return Response(
            _error_payload(
                code=exc.code,
                message=exc.message,
                details=exc.details,
                request=request,
            ),
            status=exc.status_code,
        )

    response = exception_handler(exc, context)
    if response is None:
        return None

    code = STATUS_ERROR_CODES.get(response.status_code, "SERVICE_UNAVAILABLE")
    message = STATUS_ERROR_MESSAGES.get(response.status_code, "服务暂时不可用")
    details = response.data if response.status_code == 400 else {}
    response.data = _error_payload(code=code, message=message, details=details, request=request)
    return response


def api_not_found(request, exception):
    del exception
    return JsonResponse(
        _error_payload(
            code="RESOURCE_NOT_FOUND",
            message="请求的资源不存在",
            details={},
            request=request,
        ),
        status=404,
    )
