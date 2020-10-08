from django.conf.urls import url
from django.http import HttpResponse
from django.urls import path, re_path

from . import views


urlpatterns = [
    url(r"^$", views.index),
    re_path(r"re-path.*/", views.repath_view),
    path("error/", views.view_with_error),
]
