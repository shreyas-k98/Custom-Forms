from rest_framework import serializers
from user_feedback.models import FormFields
from user_feedback.enums import InputTypeEnum


class FieldSerializer(serializers.ModelSerializer):
    """serializer to fetch fields data"""

    options = serializers.SerializerMethodField(method_name="get_options")

    class Meta:
        model = FormFields
        fields = (
            "order",
            "options",
            "field_id",
            "field_name",
            "field_type",
            "is_required",
        )

    def get_options(
        self: object, instance: object, *args: tuple, **kwargs: dict
    ) -> list[dict] | None:
        """custom method to get options"""
        if instance.field_type not in [
            InputTypeEnum.RADIO.value,
            InputTypeEnum.CHECKBOX.value,
        ]:
            return []

        return list(
            instance.option_form.all().values(
                "option_id", "option_lable", "option_value"
            )
        )
