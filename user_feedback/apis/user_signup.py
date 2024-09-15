import json
from django.views import View
from user_feedback.models import User
from django.http import HttpRequest, JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt


class UserRegistrationView(View):
    """View to register user in system"""

    http_method_names = ["post", "put"]

    def prepare_and_save_user(
        self: object, payload: dict, id: int | None = None, *args: tuple, **kwargs: dict
    ) -> User:
        """Common function to save or update user"""
        user = User.objects.get(user_id=id) if id else User()
        user.set_values(payload)
        user.save()
        return user

    def post(
        self: object, request: HttpRequest, *args: tuple, **kwargs: dict
    ) -> JsonResponse:
        """post method to register a user"""
        payload: dict = request.data
        if not all(
            [
                (email := payload.get("email")),
                (username := payload.get("username")),
                (password := payload.get("password")),
                (last_name := payload.get("name")),
                (first_namne := payload.get("name")),
            ]
        ):
            return JsonResponse({"message": "Invalid payload"}, status=400)

        all_users: list = User.objects.all().values_list("username", flat=True)
        if username in all_users:
            return JsonResponse({"message": "Username already exists"}, status=400)
        user: User = self.prepare_and_save_user(
            payload={
                "email": email,
                "username": username,
                "password": password,
                "last_name": last_name,
                "first_namne": first_namne,
            }
        )
        return JsonResponse({"message": "User saved successfully"})

    def put(
        self: object,
        request: HttpRequest,
        id: int | None = None,
        *args: tuple,
        **kwargs: dict,
    ) -> JsonResponse:
        """put method used to update data of user"""
        payload: dict = request.data
        if "username" in payload:
            return JsonResponse({"message": "Username cannot be edited"}, status=400)

        user: User = User.objects.filter(user_id=id).first()
        if not user:
            return JsonResponse({"message": "Invalid ID"}, status=400)

        user: User = self.prepare_and_save_user(payload=payload, id=id)
        return JsonResponse({"message": "User updated successfully"})
