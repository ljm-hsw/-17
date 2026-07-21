from .base import *  # noqa: F403

DEBUG = False
SECRET_KEY = env("DJANGO_SECRET_KEY")  # noqa: F405
DATABASES = {"default": env.db("DATABASE_URL")}  # noqa: F405
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS")  # noqa: F405
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
