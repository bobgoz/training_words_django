from django.urls import path

from . import views

urlpatterns = [
    path('add_word/', views.WordCreateView.as_view(), name='add_word'),
    path(
        'mark_as_active/',
        views.MarkAsActiveView.as_view(),
        name='mark_as_active',
    ),
    path('training/', views.TrainingView.as_view(), name='training'),
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
        '<int:pk_word>/confirm_delete/',
        views.ConfirmDeleteWordView.as_view(),
        name='conf_delete_word',
    ),
    path('random/', views.ShowRandomView.as_view(), name='random'),
]
