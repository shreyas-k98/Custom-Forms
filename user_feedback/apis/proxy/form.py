from django.utils import timezone
from user_feedback.models import CustomForms


class Form(CustomForms):
    """Proxy class for CustomForm"""

    class Meta:
        proxy = True

    @classmethod
    def create(
        cls: type, id: int, title: str = "", *args: tuple, **kwargs: dict
    ) -> object:
        """class method to create form in database"""
        form = cls.objects.create(
            created_by_id=id,
            updated_by_id=id,
            form_title=title,
            created_at=timezone.now(),
            updated_at=timezone.now(),
        )
        return form

    @classmethod
    def filter(cls: type, user_id: int, *args: tuple, **kwargs: dict) -> list:
        """class method to get forms creatd by user"""
        if not user_id:
            return

        forms = cls.objects.filter(created_by_id=user_id).values(
            "form_id", "form_title", "created_at"
        )
        if not forms:
            return []

        return list(forms)

    @classmethod
    def get(cls: type, form_id: int, *args: tuple, **kwargs: dict) -> object:
        """class method to get form meta using form_id"""
        if not form_id:
            return

        form = cls.objects.filter(form_id=form_id).first()
        if not form:
            return

        return form
