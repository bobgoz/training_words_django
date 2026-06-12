def clean_session(request):
    """ Очистка сессии."""
    # Очищаем сессию
    request.session.pop('training_words', None)
    request.session.pop('training_current_index', None)
    request.session.pop('training_settings', None)
    request.session.pop('training_session_id', None)
    request.session.pop('training_correct_count', None)
    request.session.pop('training_incorrect_count', None)
    request.session.pop('training_total_words', None)
