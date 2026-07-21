import re
import uuid

REQUEST_ID_PATTERN = re.compile(r"^[A-Za-z0-9_.:-]{1,128}$")


class RequestIdMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        supplied_request_id = request.headers.get("X-Request-ID", "")
        if REQUEST_ID_PATTERN.fullmatch(supplied_request_id):
            request.request_id = supplied_request_id
        else:
            request.request_id = f"req_{uuid.uuid4().hex}"

        response = self.get_response(request)
        response["X-Request-ID"] = request.request_id
        return response
