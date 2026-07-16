from django.urls import path

from . import views

app_name = "download"

urlpatterns = [
    path("download/", views.DownloadView.as_view(), name="download"),
]
