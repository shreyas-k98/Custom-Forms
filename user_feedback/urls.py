from django.urls import path
from user_feedback.apis.custom_form import AllFormsView, CustomFormView, FormMetaView
from user_feedback.apis.form_responses import CustomFormResponseView
from user_feedback.apis.session import Session
from user_feedback.apis.submit_form import FormSubmissionView
from user_feedback.apis.user_login import UserLoginView, UserLogoutView
from user_feedback.apis.user_signup import UserRegistrationView
from django.views.decorators.csrf import csrf_exempt

user_urls: list = [
    path("user/logout", UserLogoutView.as_view()),
    path("user/<int:id>", UserRegistrationView.as_view()),
    path("user/login", csrf_exempt(UserLoginView.as_view())),
    path("user/new", csrf_exempt(UserRegistrationView.as_view())),
]

form_urls: list = [
    path("forms/all", AllFormsView.as_view()),
    path("form/new", CustomFormView.as_view()),
    path("form/<int:form_id>", FormMetaView.as_view()),
    path("form/<int:form_id>/submit", FormSubmissionView.as_view()),
    path("form/<int:form_id>/responses", CustomFormResponseView.as_view()),
]

session_urls: list = [path("data/session", Session.as_view())]
