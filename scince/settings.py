import os
from pathlib import Path


# مسار المشروع الأساسي
BASE_DIR = Path(__file__).resolve().parent.parent


# مفتاح الحماية
# المفتاح الافتراضي التالي مخصص للتطوير المحلي فقط
SECRET_KEY = os.environ.get(
    "DJANGO_SECRET_KEY",
    "django-insecure-development-key-change-before-production",
)


# وضع التطوير
DEBUG = True


# النطاقات المسموح بها أثناء التطوير
ALLOWED_HOSTS = [
    "127.0.0.1",
    "localhost",
]


# تطبيقات المشروع
INSTALLED_APPS = [
    # تطبيقات Django الأساسية
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # تطبيقات دفتر العلوم الذكي
    "accounts",
    "academics",
    "activities",
    "portfolios",
    "assessment",
    "intelligence",
]


# نموذج المستخدم المخصص
AUTH_USER_MODEL = "accounts.User"


# البرمجيات الوسيطة
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
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
            ],
        },
    },
]


# تطبيق WSGI
WSGI_APPLICATION = "scince.wsgi.application"


# قاعدة البيانات
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
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


# تفعيل الترجمة والتوقيت الزمني
USE_I18N = True
USE_TZ = True


# الملفات الثابتة
STATIC_URL = "static/"


# نوع المفتاح الأساسي الافتراضي
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# عرض رسائل البريد داخل الطرفية أثناء التطوير
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"