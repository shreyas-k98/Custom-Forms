from user_feedback.apis.proxy.form import Form
from user_feedback.models import FormFields
from django.db.models import QuerySet


class Field(FormFields):

    class Meta:
        proxy = True

    allowed_field_types = ["text", "big_text", "radio", "checkbox"]

    @classmethod
    def create(
        cls: type,
        form: Form,
        field_name: str = "",
        field_type: str = "text",
        order: int = 0,
        is_required: bool = False,
        *args: tuple,
        **kwargs: dict
    ) -> object:
        """class method to create a field and add it to form"""
        field = cls.objects.create(
            form=form,
            order=order,
            field_name=field_name,
            field_type=field_type,
            is_required=is_required,
        )
        return field

    @classmethod
    def filter(
        cls: type, form: Form = {}, field_ids: list = [], *args: tuple, **kwargs: dict
    ) -> QuerySet:
        """class method to get fields in forms"""
        filters: dict = {}
        if form:
            filters.update({"form": form})
        if field_ids:
            filters.update({"field_id__in": field_ids})
        fields = cls.objects.filter(**filters)
        if not fields:
            return

        return fields
