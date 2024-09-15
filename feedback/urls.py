"""
URL configuration for feedback project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import include, path
from feedback.index import home, init
from feedback.ping import Ping
from user_feedback.urls import user_urls, form_urls, session_urls

api_urlpatterns = []
ping_urls = [path("ping", Ping.as_view())]

api_urlpatterns += user_urls
api_urlpatterns += form_urls
api_urlpatterns += ping_urls
api_urlpatterns += session_urls

urlpatterns = [
    path("api/", include(api_urlpatterns)),
    path("app/", init),
    path("", home),
]
