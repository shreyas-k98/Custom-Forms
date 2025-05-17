from django.views import View
from django.middleware.csrf import get_token
from django.http import HttpRequest, JsonResponse


class Session(View):
    """view to get session data"""

    http_method_names = ["get"]

    def get(
        self: object, request: HttpRequest, *args: tuple, **kwargs: dict
    ) -> JsonResponse:
        """get method to get session data"""
        get_token(request)
        return JsonResponse(request.session._session)
