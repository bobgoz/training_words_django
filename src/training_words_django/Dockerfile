# =============================================================================
# Этап 1: Сборка зависимостей и проекта
# =============================================================================
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim AS builder

# Отключаем загрузку Python (используем системный)
ENV UV_PYTHON_DOWNLOADS=0 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Копируем только файлы с зависимостями (для кеширования слоёв)
COPY pyproject.toml uv.lock ./

# Устанавливаем зависимости (без самого проекта)
# --frozen — используем только uv.lock, не обновляем
# --no-install-project — не устанавливаем сам проект (только зависимости)
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-project --no-editable

# Копируем весь проект
COPY src/training_words_django/ ./

# Устанавливаем сам проект
# RUN --mount=type=cache,target=/root/.cache/uv \
#     uv sync --frozen --no-editable

# =============================================================================
# Этап 2: Финальный образ (минимальный)
# =============================================================================
FROM python:3.12-slim-bookworm

# Создаём пользователя без прав root
RUN groupadd -g 1001 appgroup && \
    useradd -u 1001 -g appgroup -m -d /app -s /bin/false appuser

WORKDIR /app

# Копируем виртуальное окружение из builder
COPY --from=builder --chown=appuser:appgroup /app/.venv /app/.venv

# Копируем весь код проекта из builder
COPY --from=builder --chown=appuser:appgroup /app/ /app/

# Добавляем виртуальное окружение в PATH
ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Переключаемся на непривилегированного пользователя
USER appuser

# Открываем порт
EXPOSE 8000

# Запускаем приложение
CMD ["gunicorn", "--bind", "0.0.0.0:8000","training_words.wsgi"]