from django.core.cache import cache
from django.db.models import QuerySet
from user_feedback.models import FormFields
from user_feedback.apis.proxy.form import Form
from user_feedback.serializers import FieldSerializer


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
        **kwargs: dict,
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

    @classmethod
    def get_cached_fields(
        cls: type, form_id: int, *args: tuple, **kwargs: dict
    ) -> dict:
        """get fields present in cache"""
        cache_key: str = f"form_fields_{form_id}"
        cached_fields: dict | None = cache.get(cache_key)
        if cached_fields and isinstance(cached_fields, dict):
            return cached_fields

        fields = (
            cls.objects.filter(form__form_id=form_id)
            .prefetch_related("option_form")
            .select_related("form")
        )
        if not fields:
            return

        form = fields.first().form
        fields = FieldSerializer(fields, many=True).data
        data = {
            "fields": fields,
            "form_id": form.pk,
            "form_title": form.form_title,
        }
        cache.set(cache_key, data)
        return data
