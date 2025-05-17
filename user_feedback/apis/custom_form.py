import json
from typing import NoReturn
from django.views import View
from django.db import transaction
from django.db.models import QuerySet
from user_feedback.apis.proxy.form import Form
from user_feedback.apis.proxy.field import Field
from django.http import HttpRequest, JsonResponse
from user_feedback.apis.proxy.option import Option


class CustomFormView(View):
    """View to create custom form and save in DB"""

    http_method_names = ["post"]

    def create_option(
        self: object, option: dict, field: Field, *args: tuple, **kwargs: dict
    ) -> NoReturn:
        """method to create custom options for a field"""
        if not all(
            [
                (value := option.get("value")),
                (label := option.get("label")),
            ]
        ):
            return

        custom_option = Option.create(field, value, label)
        return custom_option

    def create_field(
        self: object, field: dict, form: Form, *args: tuple, **kwargs: dict
    ) -> Field | None:
        """method to create fields inside forms"""
        if not all(
            [
                (order := field.get("order")),
                (field_name := field.get("field_name")),
                (field_type := field.get("field_type")),
                (field_type in Field.allowed_field_types),
            ]
        ):
            return

        is_required: bool = field.get("is_required", False)
        custom_field = Field.create(form, field_name, field_type, order, is_required)
        if not all([(options := field.get("options")), (isinstance(options, list))]):
            return field

        [self.create_option(option, custom_field) for option in options]

    def post(
        self: object, request: HttpRequest, *args: tuple, **kwargs: dict
    ) -> JsonResponse:
        """post method to create custom form and store in Database"""
        payload: dict = request.data
        if not all(
            [
                (user := request.session.get("user_id")),
                (form_title := payload.get("form_title")),
                (fields := payload.get("fields")),
                isinstance(fields, list),
            ]
        ):
            return JsonResponse({"message": "Invalid Payload"})

        with transaction.atomic():
            form = Form.create(user, form_title)
            [self.create_field(field, form) for field in fields]

        return JsonResponse(
            {
                "form": {
                    "form_id": form.pk,
                    "form_title": form.form_title,
                    "created_at": form.created_at,
                }
            }
        )


class AllFormsView(View):
    """View to fetch all forms data"""

    http_method_names = ["get"]

    def get(
        self: object, request: HttpRequest, *args: tuple, **kwargs: dict
    ) -> JsonResponse:
        """get method to fetch all forms for a user"""

        if not (user_id := request.session.get("user_id")):
            return JsonResponse({"message": "Invalid Payload"}, status=400)

        forms: list = Form.filter(user_id)
        return JsonResponse({"forms": forms})


class FormMetaView(View):
    """View to get form fields dsta from Form ID"""

    http_method_names = ["get"]
    option_fields = ["radio", "checkbox"]

    def prepare_form_response(
        self: object,
        fields: QuerySet,
        options: QuerySet | list = [],
        *args: tuple,
        **kwargs: dict,
    ) -> dict:
        form_response: dict = {}
        form = fields.first() and fields.first().form
        fields: list = list(
            fields.values(
                "field_id", "field_name", "field_type", "is_required", "order"
            )
        )
        if options:
            [
                (
                    field.update({"options": options_list})
                    if (
                        options_list := list(
                            options.filter(field_id=field.get("field_id")).values(
                                "option_id", "option_lable", "option_value"
                            )
                        )
                    )
                    else None
                )
                for field in fields
            ]

        form_response.update(
            {"form_id": form.form_id, "form_title": form.form_title, "fields": fields}
        )
        return form_response

    def get(
        self: object, request: HttpRequest, form_id: int, *args: tuple, **kwargs: dict
    ) -> JsonResponse:
        """get method to fetch form meta"""
        if not all(
            [
                (form_id),
                (request.session.get("user_id")),
            ]
        ):
            return JsonResponse({"message": "Invalid Payload"}, status=400)

        fields: QuerySet = Field.objects.filter(form__form_id=form_id).select_related(
            "form"
        )
        if not fields:
            return JsonResponse({"message": "Form Do not have any fields"}, status=400)

        option_fields = fields.filter(field_type__in=self.option_fields)
        if not option_fields:
            return JsonResponse(
                {"form": self.prepare_form_response(fields, options=[])}
            )

        options: QuerySet = Option.filter(option_fields)
        return JsonResponse(self.prepare_form_response(fields, options=options))
