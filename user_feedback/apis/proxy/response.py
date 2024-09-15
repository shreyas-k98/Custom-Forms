from user_feedback.models import FormResponses


class Response(FormResponses):

    class Meta:
        proxy = True

    @classmethod
    def create(cls: type, payload: dict, *args: tuple, **kwargs: dict) -> object:
        if not payload:
            return
        response = cls.objects.create(**payload)
        return response
