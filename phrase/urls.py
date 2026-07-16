from django.urls import path

from . import views

urlpatterns = [
    path("new_phrase/", views.PhraseCreateView.as_view(), name="add_phrase"),
    path(
        "phrase_manager/",
        views.PhraseManagerView.as_view(),
        name="phrase_manager",
    ),
    path(
        "phrase_manager/active/",
        views.ShowActivePhrasesView.as_view(),
        name="active_phrases",
    ),
    path(
        "phrase_manager/inactive/",
        views.ShowInactivePhrasesView.as_view(),
        name="inactive_phrases",
    ),
    path(
        "phrase_manager/learned_phrases/",
        views.ShowLearnedPhrasesView.as_view(),
        name="learned_phrases",
    ),
    path(
        "phrase/<int:pk_phrase>/detail/",
        views.DetailPhraseView.as_view(),
        name="phrase_detail",
    ),
    path(
        "phrase/<int:pk_phrase>/delete/",
        views.DeletePhraseView.as_view(),
        name="delete_phrase",
    ),
    path(
        "phrase/<int:pk_phrase>/edit/",
        views.EditPhraseView.as_view(),
        name="edit_phrase",
    ),
]
