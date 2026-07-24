from apps.common.schema import SchemaAPIView as APIView

from .api import api_response


class HealthView(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request):
        return api_response(request, {"status": "ok"})
