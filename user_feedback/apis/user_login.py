import json
from django.views import View
from user_feedback.models import User
from django.http import HttpRequest, JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt


class UserLoginView(View):
    """View to handle user login"""

    http_method_names = ["post"]

    def post(
        self: object, request: HttpRequest, *args: tuple, **kwargs: dict
    ) -> JsonResponse:
        """post method to login into system"""
        payload: dict = request.data
        if not all(
            [
                (username := payload.get("username")),
                (password := payload.get("password")),
            ]
        ):
            return JsonResponse(
                {"message": "Valid username and password are required"}, status=400
            )

        user: User = User.objects.filter(
            username=username, password=password, is_active=True
        ).first()
        if not user:
            return JsonResponse({"message": "Invalid credentials"}, status=400)

        request.session.update(
            {
                "user_id": user.user_id,
                "email": user.email or "",
                "last_name": user.last_name or "",
                "first_name": user.first_name or "",
            }
        )
        return JsonResponse({"session": request.session._session})


class UserLogoutView(View):
    """View to handle user logout"""

    def get(
        self: object, request: HttpRequest, *args: tuple, **kwargs: dict
    ) -> JsonResponse:
        """get method to clear user session"""
        session = request.session
        if not session.get("user_id"):
            return JsonResponse({})

        request.session.flush()
        return JsonResponse({"message": "User logged out successfully"})
