from django.urls import path

from . import views

urlpatterns = [
    path("new_phrase/", views.PhraseCreateView.as_view(), name="add_phrase"),
    path(
        "phrase_manager/",
        views.PhraseManagerView.as_view(),
        name="phrase_manager",
    ),
    path(""),
]
