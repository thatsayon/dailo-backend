import os
from pathlib import Path
from celery import Celery
import environ

# Explicitly load .env so Django settings can read env vars
# (Celery worker is a fresh process — it doesn't inherit the shell environment)
_BASE_DIR = Path(__file__).resolve().parent.parent
environ.Env.read_env(_BASE_DIR / ".env")

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.dev")

app = Celery("dailo")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
