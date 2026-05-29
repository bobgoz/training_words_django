from django.urls import path

from . import views

urlpatterns = [
    path('add_word/', views.WordCreateView.as_view(), name='add_word'),
    path(
        'reset-learned/',
        views.ResetLearnedWordsView.as_view(),
        name='reset_learned_words',
    ),
    path('training/', views.TrainingView.as_view(), name='training'),
    path(
        'training_hard/',
        views.TrainingHardView.as_view(),
        name='training_hard',
    ),
    path(
        'training_no_active/',
        views.TrainingNoActiveView.as_view(),
        name='training_no_active',
    ),
    path(
        'show_learned_words/',
        views.ShowLearnedView.as_view(),
        name='show_learned_words',
    ),
    path(
        '<int:pk_word>/detail/',
        views.DetailWordView.as_view(),
        name='detail',
    ),
    path(
        '<int:pk_word>/edit/',
        views.EditWordView.as_view(),
        name='edit_word',
    ),
    path(
        '<int:pk_word>/delete/',
        views.DeleteWordView.as_view(),
        name='delete_word',
    ),
    path(
        'search',
        views.SearchView.as_view(),
        name='search',
    ),
    path(
        'train/setup/',
        views.TrainingSetupView.as_view(),
        name='training_setup',
    ),
    path('train/card/', views.TrainCardView.as_view(), name='train_card'),
    path(
        'train/answer/', views.TrainAnswerView.as_view(), name='train_answer'
    ),
    path(
        'train/complete/',
        views.TrainCompleteView.as_view(),
        name='train_complete',
    ),
]
