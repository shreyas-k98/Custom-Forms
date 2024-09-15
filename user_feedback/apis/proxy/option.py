from django.db.models import QuerySet
from typing import Any
from user_feedback.apis.proxy.field import Field
from user_feedback.models import Options


class Option(Options):

    class Meta:
        proxy = True

    @classmethod
    def create(
        cls: type,
        field: Field,
        value: Any = "",
        label: str = "",
        *args: tuple,
        **kwargs: dict
    ) -> object:
        option = cls.objects.create(
            field=field,
            option_lable=label,
            option_value=value,
        )
        return option

    @classmethod
    def filter(
        cls: type, option_fields: QuerySet, *args: tuple, **kwargs: dict
    ) -> QuerySet | list:
        """class method to fetch options"""
        option_field_ids: list = [field.field_id for field in option_fields]
        if not option_field_ids:
            return []

        options = cls.objects.filter(field_id__in=option_field_ids)
        if not options:
            return []

        return options
