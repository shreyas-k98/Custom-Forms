from celery import shared_task
from django.conf import settings
from user_feedback.models import User
from django.core.mail import send_mail


@shared_task
def send_registration_email(user_id: int, *args: tuple, **kwargs: dict) -> None:
    """Celery task to send welcome email to user"""
    try:
        user = User.objects.get(user_id=user_id)
        subject: str = f"Welcome to the Custom Forms Project, {user.first_name}"
        body: str = (
            f"""
                Thank you {user.first_name} for creating an account in Custom Forms Project. 
                You have successfully registered in Custom Forms project with the username as {user.username}. Feel free to explore the project.

                Fetures available - 
                    1. Generate custom forms to collect data from users
                    2. Copy and share the link of the form
                    3. Download user response in Excel format.
                
                Upcomming features - 
                    1. Share copy of response over an email
                    2. View Responses on UI
            """
        )
        email_sent: int | None = send_mail(
            message=body,
            subject=subject,
            fail_silently=False,
            recipient_list=[user.email],
            from_email=settings.EMAIL_HOST_USER,
        )
        if not email_sent:
            print(f"Failed to send Email Message. output - {email_sent}")
            return
        
        print(f"Sent mssage successfully. output - {email_sent}")
    except Exception as e:
        print(f"Failed to send message with an exception {e}")
