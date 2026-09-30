# config/settings/dev.py
import environ

from .base import *  # noqa: F403

env = environ.Env()
environ.Env.read_env(BASE_DIR / ".env")  # noqa: F405

# Explicitly use env.bool to enforce true boolean casting
DEBUG = env.bool("DJANGO_DEBUG", default=True)

SECRET_KEY = env("DJANGO_SECRET_KEY", default="django-insecure-dev-key-placeholder")

ALLOWED_HOSTS = ["localhost", "127.0.0.1"]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",  # noqa: F405
    }
}

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "unique-snowflake",
    }
}
