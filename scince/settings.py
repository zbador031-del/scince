import os
from pathlib import Path

import dj_database_url
from dotenv import load_dotenv


# المسار الأساسي للمشروع
BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(
    BASE_DIR / ".env",
    override=True,
)
# مفتاح الحماية
# القيمة الافتراضية التالية للتطوير المحلي فقط
SECRET_KEY = os.environ.get(
    "DJANGO_SECRET_KEY",
    "django-insecure-development-key-change-before-production",
)


# وضع التطوير المحلي
DEBUG = os.environ.get("DEBUG", "True").lower() == "true"


# النطاقات المسموح بها محليًا
ALLOWED_HOSTS = [
    "127.0.0.1",
    "localhost",
]

if render_hostname := os.environ.get("RENDER_EXTERNAL_HOSTNAME"):
    ALLOWED_HOSTS.append(render_hostname)

CSRF_TRUSTED_ORIGINS = [
    origin.strip()
    for origin in os.environ.get("CSRF_TRUSTED_ORIGINS", "").split(",")
    if origin.strip()
]

if render_hostname:
    CSRF_TRUSTED_ORIGINS.append(f"https://{render_hostname}")


# التطبيقات المثبتة
INSTALLED_APPS = [
    # تطبيقات Django الأساسية
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # تطبيقات دفتر العلوم الذكي
    "accounts.apps.AccountsConfig",
    "academics.apps.AcademicsConfig",
    "activities.apps.ActivitiesConfig",
    "portfolios.apps.PortfoliosConfig",
    "assessment.apps.AssessmentConfig",
    "intelligence.apps.IntelligenceConfig",
]


# نموذج المستخدم المخصص
AUTH_USER_MODEL = "accounts.User"


# البرمجيات الوسيطة
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]


# ملف الروابط الرئيسي
ROOT_URLCONF = "scince.urls"


# إعدادات القوالب
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            BASE_DIR / "templates",
        ],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "intelligence.context_processors.monthly_honor_ticker",
            ],
        },
    },
]


# تطبيق WSGI
WSGI_APPLICATION = "scince.wsgi.application"


# قاعدة البيانات
DATABASES = {
    "default": dj_database_url.config(
        default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}",
        conn_max_age=600,
        conn_health_checks=True,
    )
}


# التحقق من قوة كلمات المرور
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "UserAttributeSimilarityValidator"
        ),
    },
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "MinimumLengthValidator"
        ),
    },
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "CommonPasswordValidator"
        ),
    },
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "NumericPasswordValidator"
        ),
    },
]


# اللغة العربية
LANGUAGE_CODE = "ar"


# توقيت المملكة العربية السعودية
TIME_ZONE = "Asia/Riyadh"


# الترجمة والتوقيت
USE_I18N = True
USE_TZ = True


# الملفات الثابتة مثل CSS وJavaScript
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_STORAGE = (
    "whitenoise.storage.CompressedStaticFilesStorage"
)


# الملفات المرفوعة مثل الصور والفيديوهات والمستندات
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"


# نوع المفتاح الأساسي الافتراضي
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# عرض رسائل البريد داخل PowerShell أثناء التطوير
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# إعدادات تسجيل الدخول والخروج
LOGIN_URL = "accounts:login"
LOGIN_REDIRECT_URL = "accounts:dashboard"
LOGOUT_REDIRECT_URL = "accounts:home"

STORAGES = {
    "default": {
        "BACKEND": (
            "cloudinary_storage.storage."
            "MediaCloudinaryStorage"
        ),
    },
    "staticfiles": {
        "BACKEND": (
            "whitenoise.storage."
            "CompressedStaticFilesStorage"
        ),
    },
}

if not os.environ.get("CLOUDINARY_URL"):
    STORAGES["default"] = {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    }

if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    SECURE_SSL_REDIRECT = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
