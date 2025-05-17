from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.

BaseModel = models.Model


class User(AbstractUser):
    username = models.CharField(max_length=100, db_column="username")
    user_id = models.AutoField(primary_key=True)
    groups = models.ManyToManyField(
        "auth.Group", related_name="user_feedback_user_groups", blank=True
    )
    user_permissions = models.ManyToManyField(
        "auth.Permission", related_name="user_feedback_user_permissions", blank=True
    )

    class Meta:
        db_table = "User"

    def set_values(self, values):
        """set values to report values"""
        if not values or not isinstance(values, dict):
            return self

        to_update = {f: v for f, v in values.items()}
        for field, value in to_update.items():
            setattr(
                self,
                field,
                value.strip() if isinstance(value, str) else value,  # noqa F821
            )
        return self


class CustomForms(BaseModel):
    form_id = models.AutoField(primary_key=True)
    form_title = models.CharField(max_length=100, db_column="form_title")
    created_by = models.ForeignKey(
        to=User,
        null=False,
        blank=False,
        on_delete=models.DO_NOTHING,
        related_name="created_user",
    )
    created_at = models.DateTimeField(db_column="created_at")
    updated_by = models.ForeignKey(
        to=User,
        null=False,
        blank=False,
        on_delete=models.DO_NOTHING,
        related_name="updated_user",
    )
    updated_at = models.DateTimeField(db_column="updated_at")

    class Meta:
        db_table = "CustomForms"


class FormFields(BaseModel):
    field_id = models.AutoField(primary_key=True)
    form = models.ForeignKey(
        to=CustomForms,
        null=False,
        blank=False,
        on_delete=models.DO_NOTHING,
        related_name="custom_form",
    )
    field_name = models.CharField(max_length=100, db_column="field_name")
    field_type = models.CharField(max_length=50, db_column="field_type")
    is_required = models.BooleanField(default=False, db_column="is_required")
    order = models.IntegerField(default=0, db_column="order")

    class Meta:
        db_table = "FormFields"


class Options(BaseModel):
    option_id = models.AutoField(primary_key=True)
    field = models.ForeignKey(
        to=FormFields,
        null=False,
        blank=False,
        on_delete=models.DO_NOTHING,
        related_name="option_form",
    )
    option_lable = models.CharField(max_length=100, db_column="option_lable")
    option_value = models.CharField(max_length=100, db_column="option_value")

    class Meta:
        db_table = "Options"


class FormResponses(BaseModel):
    response_id = models.AutoField(primary_key=True)
    filled_by = models.ForeignKey(
        to=User,
        null=False,
        blank=False,
        on_delete=models.DO_NOTHING,
        related_name="filled_response",
    )
    form = models.ForeignKey(
        to=CustomForms,
        null=False,
        blank=False,
        on_delete=models.DO_NOTHING,
        related_name="form_response",
    )

    class Meta:
        db_table = "FormResponses"


class TextFieldResponses(BaseModel):
    """model to store text fields"""

    response = models.ForeignKey(
        to=FormResponses,
        null=False,
        blank=False,
        default=None,
        related_name="related_response",
        on_delete=models.DO_NOTHING,
    )
    field = models.ForeignKey(
        to=FormFields,
        null=False,
        blank=False,
        related_name="related_fields",
        on_delete=models.DO_NOTHING,
    )
    form = models.ForeignKey(
        to=CustomForms,
        null=False,
        blank=False,
        related_name="forms_set",
        on_delete=models.DO_NOTHING,
    )
    response_text = models.TextField(null=True, blank=True)

    class Meta:
        db_table = "TextFieldResponses"

    @classmethod
    def save_response(
        cls: type,
        response_id: int,
        form_id: int,
        field: dict,
        *args: tuple,
        **kwargs: dict
    ) -> None:
        """save response for text field"""
        field_id, response_text = field.get("id"), field.get("response_text")
        if not all([field_id, response_text]):
            return None

        cls.objects.create(
            form_id=form_id,
            field_id=field_id,
            response_id=response_id,
            response_text=response_text,
        )

    @classmethod
    def get_response_value(
        cls: type,
        response: FormResponses,
        field: FormFields,
        *args: tuple,
        **kwargs: dict
    ) -> str:
        """get response value for text field"""
        field_id: int = field.get("field_id")
        resp = response.related_response.filter(field_id=field_id).first()
        return resp.response_text if resp else ""


class OptionFieldResponses(BaseModel):
    """model to store option fields (radio, checkbox)"""

    response = models.ForeignKey(
        to=FormResponses,
        null=False,
        blank=False,
        related_name="related_response_option",
        on_delete=models.DO_NOTHING,
    )
    field = models.ForeignKey(
        to=FormFields,
        null=False,
        blank=False,
        related_name="related_fields_options",
        on_delete=models.DO_NOTHING,
    )
    form = models.ForeignKey(
        to=CustomForms,
        null=False,
        blank=False,
        related_name="option_field_response",
        on_delete=models.DO_NOTHING,
    )
    selected_option = models.ForeignKey(
        to=Options,
        null=False,
        related_name="related_options",
        on_delete=models.DO_NOTHING,
    )

    class Meta:
        db_table = "OptionFieldResponses"

    @classmethod
    def save_response(
        cls: type,
        response_id: int,
        form_id: int,
        field: dict,
        *args: tuple,
        **kwargs: dict
    ) -> None:
        """save responses for option fields like radio and checkbox field"""
        field_id, options, selected_option = (
            field.get("id"),
            field.get("options", []),
            field.get("selected_option"),
        )
        if not any(
            [
                isinstance(options, list),
                isinstance(selected_option, int),
            ]
        ):
            return None

        options: list[int] = [selected_option] if selected_option else options
        cls.objects.bulk_create(
            [
                cls(
                    form_id=form_id,
                    field_id=field_id,
                    response_id=response_id,
                    selected_option_id=option_id,
                )
                for option_id in options
            ]
        )

    @classmethod
    def get_response_value(
        cls: type,
        response: FormResponses,
        field: FormFields,
        *args: tuple,
        **kwargs: dict
    ) -> str:
        """get response value for option fields (radio, checkbox)"""
        field_id: int = field.get("field_id")
        resp = response.related_response_option.filter(field_id=field_id).values_list(
            "selected_option__option_value", flat=True
        )
        option_field_values: str = ", ".join(resp)
        return option_field_values or ""
