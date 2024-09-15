from django.http import HttpRequest, JsonResponse
from django.views import View


class Ping(View):

    def get(
        self: object, request: HttpRequest, *args: tuple, **kwargs: dict
    ) -> JsonResponse:
        return JsonResponse({"message": "pong"})
