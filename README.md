# Dailo Backend

A Django REST Framework backend for the Dailo platform.

## Requirements

- Python 3.12+
- PostgreSQL
- Redis (for Celery)

## Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Copy and configure environment variables
cp .env.example .env

# Apply migrations
python manage.py migrate

# Create a superuser
python manage.py createsuperuser
```

## Running the Server

```bash
python manage.py runserver
```

## Running the Celery Worker

```bash
celery -A config worker -l info
```

> The Celery worker is required for background tasks such as sending OTP verification emails.

## Running Celery Beat (Scheduled Tasks)

```bash
celery -A config beat -l info
```
