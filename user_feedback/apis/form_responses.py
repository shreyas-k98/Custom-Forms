from xlwt import Workbook
from django.views import View
from django.db.models import QuerySet
from user_feedback.apis.proxy.form import Form
from user_feedback.apis.proxy.field import Field
from user_feedback.apis.proxy.response import Response
from django.http import HttpRequest, HttpResponse, JsonResponse


class CustomFormResponseView(View):
    """View to fetch all responses of a form and gnerate an excel to export responses"""

    def get(
        self: object, request: HttpRequest, form_id: int, *args: tuple, **kwargs: dict
    ) -> HttpResponse | JsonResponse:
        """method to get all responses"""
        if not all([(form_id), (user_id := request.session.get("user_id"))]):
            return JsonResponse({"message": "Invalid Payload"}, status=400)

        form: Form = Form.get(form_id)
        if not form:
            return JsonResponse({"message": "Invalid form id"}, status=400)

        if not form.created_by.user_id == user_id:
            return JsonResponse(
                {"message": "Form responses can only be exported by Creator"},
                status=400,
            )

        fields: list = list(Field.filter(form).values("field_id", "field_name"))
        field_ids: list = [field.get("field_id") for field in fields]
        form_responses: QuerySet = Response.objects.filter(form_id=form.form_id)
        response_uuids: list = list(
            set(form_responses.values_list("response_uuid", flat=True))
        )
        work_book: Workbook = Workbook()
        work_sheet = work_book.add_sheet("form-responses.xls")
        work_sheet.write(0, 0, "Response Added By")
        for index, item in enumerate(fields):
            field_id: int = item.get("field_id")
            field_name: str = item.get("field_name")
            work_sheet.write(0, index + 1, field_name)

        row_index: int = 1
        for ind, itr in enumerate(response_uuids):
            field_by: str = "unknown"
            form_response: Response = form_responses.filter(response_uuid=itr).first()
            if form_response:
                field_by = form_response.filled_by.username

            work_sheet.write(row_index, 0, field_by)
            for i, f in enumerate(field_ids):
                row_data: Response = form_responses.filter(
                    response_uuid=itr, field_id=f
                ).first()
                if not row_data:
                    continue

                data = ""
                if row_data.field.field_type in ["text", "checkbox"]:
                    data = row_data.response_text

                if row_data.field.field_type == "radio":
                    data = row_data.option.option_value

                work_sheet.write(row_index, i + 1, data)
            row_index += 1

        response: HttpResponse = HttpResponse(content_type="application/vnd.ms-excel")
        response["Content-Disposition"] = "attachment; filename=form-responses.xls"
        work_book.save(response)
        return response
