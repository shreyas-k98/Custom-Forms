import json
from typing import Any, NoReturn, Callable

from django.http import HttpRequest, JsonResponse


class CustomMiddleWare:
    """Custom middleware to handle request"""

    guest_urls = ["/api/user/login", "/api/user/new", "/api/", "/api/data/session"]

    def __init__(self: object, get_response: Callable) -> NoReturn:
        """init method for middleware"""
        self.get_response = get_response

    def __call__(self: object, request: HttpRequest) -> Any:
        if (
            not request.method == "GET"
            and not request.session.get("user_id")
            and request.path not in self.guest_urls
        ):
            return JsonResponse({"message": "Authentication Error"}, status=400)
        if request.body:
            request.data = json.loads(request.body or "{}")
        response = self.get_response(request)
        return response
