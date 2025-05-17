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
from user_feedback.enums import InputTypeEnum
from user_feedback.models import FormResponses, OptionFieldResponses, TextFieldResponses


class FormSubmissionView(View):
    """View to handle form submission"""

    http_method_names: list = ["post"]
    input_type_mapper: dict = {
        InputTypeEnum.TEXT.value: TextFieldResponses,
        InputTypeEnum.RADIO.value: OptionFieldResponses,
        InputTypeEnum.CHECKBOX.value: OptionFieldResponses,
    }

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

        if not payload.get("fields"):
            return JsonResponse({"message" "Invalid payload"}, status=400)

        fields: list = payload.get("fields", [])
        with transaction.atomic():
            response = FormResponses.objects.create(
                form_id=form_id, filled_by_id=user_id
            )
            for field in fields:
                field_type = field.get("type")
                field_class = self.input_type_mapper.get(field_type)
                field_class.save_response(
                    field=field,
                    form_id=form_id,
                    response_id=response.response_id,
                )

        return JsonResponse({"message": "Form submitted successfully"})
