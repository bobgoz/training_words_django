FROM python:3.12

WORKDIR /app

COPY requirements.prod.txt .

RUN apt update && \
    apt install -y nano && \
    pip install -r requirements.prod.txt --no-cache-dir

COPY . .

CMD [ "gunicorn", "--bind", "0.0.0.0:8000", "training_words.wsgi"]