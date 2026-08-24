import os
from pathlib import Path


# المسار الأساسي للمشروع
BASE_DIR = Path(__file__).resolve().parent.parent


# مفتاح الحماية
# القيمة الافتراضية التالية للتطوير المحلي فقط
SECRET_KEY = os.environ.get(
    "DJANGO_SECRET_KEY",
    "django-insecure-development-key-change-before-production",
)


# وضع التطوير المحلي
DEBUG = True


# النطاقات المسموح بها محليًا
ALLOWED_HOSTS = [
    "127.0.0.1",
    "localhost",
]


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


# الترجمة والتوقيت
USE_I18N = True
USE_TZ = True


# الملفات الثابتة مثل CSS وJavaScript
STATIC_URL = "/static/"


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