from django.urls import path

from . import views

urlpatterns = [
    path("new_word/", views.WordCreateView.as_view(), name="add_word"),
    path(
        "reset_learned/",
        views.ResetLearnedWordsView.as_view(),
        name="reset_learned_words",
    ),
    path(
        "manager/active/",
        views.ShowActiveWordsView.as_view(),
        name="active_words",
    ),
    path(
        "manager/inactive/",
        views.ShowInactiveWordsView.as_view(),
        name="inactive_words",
    ),
    path(
        "manager/learned/",
        views.ShowLearnedView.as_view(),
        name="learned_words",
    ),
    path(
        "<int:pk_word>/detail/",
        views.DetailWordView.as_view(),
        name="detail",
    ),
    path(
        "<int:pk_word>/edit/",
        views.EditWordView.as_view(),
        name="edit_word",
    ),
    path(
        "<int:pk_word>/delete/",
        views.DeleteWordView.as_view(),
        name="delete_word",
    ),
    path("search", views.SearchView.as_view(), name="search"),
    path(
        "train/setup/",
        views.TrainingSetupView.as_view(),
        name="training_setup",
    ),
    path("train/card/", views.TrainCardView.as_view(), name="train_card"),
    path("train/answer/", views.TrainAnswerView.as_view(), name="train_answer"),
    path(
        "train/complete/",
        views.TrainCompleteView.as_view(),
        name="train_complete",
    ),
    path(
        "word_manager/",
        views.WordManagerView.as_view(),
        name="word_manager",
    ),
]
