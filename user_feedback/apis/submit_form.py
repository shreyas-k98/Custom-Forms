import json
import uuid
from typing import NoReturn
from django.views import View
from django.db import transaction
from django.db.models import QuerySet
from user_feedback.apis.proxy.form import Form
from user_feedback.apis.proxy.field import Field
from django.http import HttpRequest, JsonResponse
from user_feedback.apis.proxy.option import Option
from user_feedback.apis.proxy.response import Response


class FormSubmissionView(View):
    """View to handle form submission"""

    http_method_names = ["post"]
    fields_query_set = None
    option_fields = ["radio", "checkbox"]
    text_fields = ["text", "big_text"]

    def save_form_response(
        self: object,
        user_id: int,
        form_id: int,
        field: dict,
        *args: tuple,
        **kwargs: dict,
    ) -> NoReturn:
        id = field.get("id")
        fields_query_set = self.fields_query_set or Field.filter(field_ids=id)
        custom_field: Field = fields_query_set.filter(field_id=id).first()
        if not custom_field:
            return

        custom_field_type: str = custom_field.field_type
        if not custom_field_type in Field.allowed_field_types:
            return

        respomse_payload: dict = {}
        if "option_id" in field:
            respomse_payload.update({"option_id": field.get("option_id")})

        if "response_text" in field:
            respomse_payload.update({"response_text": field.get("response_text")})

        respomse_payload.update(
            {
                "filled_by_id": user_id,
                "form_id": form_id,
                "field_id": id,
                "response_uuid": self.uuid,
            }
        )
        response: Response = Response.create(respomse_payload)
        return response

    def post(
        self: object, request: HttpRequest, form_id: int, *args: tuple, **kwargs: dict
    ) -> JsonResponse:
        """post method to submit form response"""
        if not all(
            [
                (form_id),
                (payload := request.data),
                isinstance(payload, dict),
                (user_id := request.session.get("user_id")),
            ]
        ):
            return JsonResponse({"message" "Invalid payload"}, status=400)

        fields: dict = payload.get("fields", [])
        if not isinstance(fields, list):
            return JsonResponse({"message" "Invalid payload"}, status=400)

        field_ids = [field.get("id") for field in fields]
        fields_query_set = Field.filter(field_ids=field_ids)
        self.fields_query_set = fields_query_set
        self.uuid = uuid.uuid4()
        with transaction.atomic():
            [self.save_form_response(user_id, form_id, field) for field in fields]
        return JsonResponse({"message": "Form response saved successfully"})
