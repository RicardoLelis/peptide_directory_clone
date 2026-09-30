# config/settings/prod.py
import environ

from .base import *

env = environ.Env()

# 1. Core Security Settings
SECRET_KEY = env("DJANGO_SECRET_KEY")
DEBUG = False

# Separate multiple domains using commas in your environment variables (e.g., example.com,://example.com)
ALLOWED_HOSTS = env.list("DJANGO_ALLOWED_HOSTS")

# 2. Database Management
# Expects a standard connection string (e.g., postgres://user:password@host:port/dbname)
DATABASES = {"default": env.db("DATABASE_URL")}

# 3. Security Hardening (SSL/HTTPS redirection)
SECURE_SSL_REDIRECT = env.bool("DJANGO_SECURE_SSL_REDIRECT", default=True)
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# HSTS Settings (Only activates if SSL redirect is enabled)
if SECURE_SSL_REDIRECT:
    SECURE_HSTS_SECONDS = 31536000  # 1 year
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True

# 4. Static Files & Media Performance Optimization
# Ensure whitenoise is placed right at the top of MIDDLEWARE for high performance
_SECURITY = "django.middleware.security.SecurityMiddleware"
_WHITENOISE = "whitenoise.middleware.WhiteNoiseMiddleware"

if _WHITENOISE not in MIDDLEWARE:
    MIDDLEWARE.insert(MIDDLEWARE.index(_SECURITY) + 1, _WHITENOISE)

# Tells Whitenoise where to look for collected production assets
STATIC_ROOT = BASE_DIR / "staticfiles"

# Compresses static files and generates unique cache hashes for browser optimization
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"},
}

# Media configuration for user-uploaded assets
MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

# 5. Production Caching (Uses standard database cache fallback; upgrade to Redis if needed)
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.db.DatabaseCache",
        "LOCATION": "django_cache_table",
    }
}
