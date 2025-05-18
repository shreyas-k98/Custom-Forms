from django.dispatch import receiver
from user_feedback.models import User
from django.db.models.signals import post_save
from user_feedback.tasks import send_registration_email


@receiver(post_save, sender=User)
def user_after_save(
    instance: User, created: bool, *args: tuple, **kwargs: dict
) -> None:
    """after save for user to trigger celery task"""
    if not all([created, instance.email]):
        return

    send_registration_email.apply_async(args=[instance.pk], countdown=10)
