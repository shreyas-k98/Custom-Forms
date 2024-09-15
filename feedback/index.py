from django.middleware.csrf import get_token
from django.shortcuts import redirect, render
from django.http import HttpRequest, HttpResponse


def init(request: HttpRequest, *args: tuple, **kwargs: dict) -> HttpResponse:
    """method to render app using static file"""
    get_token(request)
    return render(request=request, template_name="index.html")


def home(request: HttpRequest, *args: tuple, **kwargs: dict) -> HttpResponse:
    """method to redirect to app/"""
    return redirect(to="app/")
