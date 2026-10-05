FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN groupadd -r -g 10001 app \
 && useradd -r -u 10001 -g app app \
 && mkdir -p /data /app/staticfiles \
 && chown -R app:app /data /app/staticfiles

USER app

RUN SECRET_KEY=build-only python manage.py collectstatic --noinput

EXPOSE 8000
