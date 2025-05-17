from xlwt import Workbook
from django.views import View
from django.db.models import QuerySet
from user_feedback.apis.proxy.form import Form
from user_feedback.apis.proxy.field import Field
from user_feedback.apis.proxy.response import Response
from django.http import HttpRequest, HttpResponse, JsonResponse

from user_feedback.enums import InputTypeEnum
from user_feedback.models import FormResponses, OptionFieldResponses, TextFieldResponses


class CustomFormResponseView(View):
    """View to fetch all responses of a form and gnerate an excel to export responses"""

    input_type_mapper: dict = {
        InputTypeEnum.TEXT.value: TextFieldResponses,
        InputTypeEnum.RADIO.value: OptionFieldResponses,
        InputTypeEnum.CHECKBOX.value: OptionFieldResponses,
    }

    def get(
        self: object, request: HttpRequest, form_id: int, *args: tuple, **kwargs: dict
    ) -> HttpResponse | JsonResponse:
        """method to get all responses"""
        if not all([request.session.get("user_id"), form_id]):
            return JsonResponse({"message": "Invalid Session"}, status=400)

        form: Form = Form.objects.get(form_id=form_id)
        if form.created_by_id != request.session.get("user_id"):
            return JsonResponse(
                {"message": "Response can only be downloaded by form owner"}, status=400
            )

        responses = (
            FormResponses.objects.filter(form_id=form_id)
            .select_related("form")
            .prefetch_related(
                "related_response",
                "related_response_option",
                "related_response_option__selected_option",
            )
        )
        form_fields = Field.objects.filter(form_id=form_id).values(
            "field_id", "field_name", "field_type"
        )
        work_book: Workbook = Workbook()
        work_sheet = work_book.add_sheet("form-responses.xls")
        work_sheet.write(0, 0, "Response Added By")
        for index, item in enumerate(form_fields):
            field_name: str = item.get("field_name")
            work_sheet.write(0, index + 1, field_name)

        row_index: int = 1
        for index, item in enumerate(responses):
            response_submitted_by: str = (
                item.filled_by.first_name or item.filled_by.username
            )
            work_sheet.write(row_index, 0, response_submitted_by)
            for field_index, field_item in enumerate(form_fields):
                field_type: str = field_item.get("field_type")
                field_class: type = self.input_type_mapper.get(field_type)
                value: str = field_class.get_response_value(
                    response=item, field=field_item
                )
                if not value:
                    continue

                work_sheet.write(row_index, field_index + 1, value)

            row_index += 1

        response: HttpResponse = HttpResponse(content_type="application/vnd.ms-excel")
        response["Content-Disposition"] = "attachment; filename=form-responses.xls"
        work_book.save(response)
        return response
