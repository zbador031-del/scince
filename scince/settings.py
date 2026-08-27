import os
from pathlib import Path

import dj_database_url
from django.core.exceptions import ImproperlyConfigured
from dotenv import load_dotenv


# المسار الأساسي للمشروع
BASE_DIR = Path(__file__).resolve().parent.parent


# تحميل متغيرات التطوير المحلي فقط
load_dotenv(
    BASE_DIR / ".env",
    override=True,
)


def env_bool(name, default=False):
    """قراءة القيم المنطقية من متغيرات البيئة."""

    value = os.environ.get(
        name,
        str(default),
    )

    return value.strip().lower() in {
        "1",
        "true",
        "yes",
        "on",
    }


def env_list(name):
    """تحويل متغير مفصول بفواصل إلى قائمة."""

    return [
        item.strip()
        for item in os.environ.get(
            name,
            "",
        ).split(",")
        if item.strip()
    ]


# وضع التشغيل
DEBUG = env_bool(
    "DEBUG",
    default=True,
)


# مفتاح الحماية
SECRET_KEY = os.environ.get(
    "DJANGO_SECRET_KEY",
    "",
).strip()

if not SECRET_KEY:
    if DEBUG:
        SECRET_KEY = (
            "django-insecure-local-development-"
            "key-change-before-production"
        )
    else:
        raise ImproperlyConfigured(
            "يجب تعريف DJANGO_SECRET_KEY في بيئة الإنتاج."
        )


# نطاق Render عند النشر
RENDER_EXTERNAL_HOSTNAME = os.environ.get(
    "RENDER_EXTERNAL_HOSTNAME",
    "",
).strip()


# النطاقات المسموح بها
ALLOWED_HOSTS = [
    "127.0.0.1",
    "localhost",
]

for host in env_list("ALLOWED_HOSTS"):
    if host not in ALLOWED_HOSTS:
        ALLOWED_HOSTS.append(host)

if (
    RENDER_EXTERNAL_HOSTNAME
    and RENDER_EXTERNAL_HOSTNAME
    not in ALLOWED_HOSTS
):
    ALLOWED_HOSTS.append(
        RENDER_EXTERNAL_HOSTNAME
    )


# المصادر الموثوقة لحماية CSRF
CSRF_TRUSTED_ORIGINS = env_list(
    "CSRF_TRUSTED_ORIGINS"
)

if RENDER_EXTERNAL_HOSTNAME:
    render_origin = (
        f"https://{RENDER_EXTERNAL_HOSTNAME}"
    )

    if (
        render_origin
        not in CSRF_TRUSTED_ORIGINS
    ):
        CSRF_TRUSTED_ORIGINS.append(
            render_origin
        )


# التطبيقات المثبتة
INSTALLED_APPS = [
    # تطبيقات Django الأساسية
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",

    # تخزين الملفات عبر Cloudinary
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
        "BACKEND": (
            "django.template.backends.django."
            "DjangoTemplates"
        ),
        "DIRS": [
            BASE_DIR / "templates",
        ],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                (
                    "django.template.context_processors."
                    "request"
                ),
                (
                    "django.contrib.auth."
                    "context_processors.auth"
                ),
                (
                    "django.contrib.messages."
                    "context_processors.messages"
                ),
                (
                    "intelligence.context_processors."
                    "monthly_honor_ticker"
                ),
            ],
        },
    },
]


# تطبيق WSGI
WSGI_APPLICATION = "scince.wsgi.application"


# قاعدة البيانات
DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "",
).strip()

if DATABASE_URL:
    DATABASES = {
        "default": dj_database_url.parse(
            DATABASE_URL,
            conn_max_age=600,
            conn_health_checks=True,
        )
    }
else:
    if not DEBUG:
        raise ImproperlyConfigured(
            "يجب تعريف DATABASE_URL في بيئة الإنتاج."
        )

    DATABASES = {
        "default": {
            "ENGINE": (
                "django.db.backends.sqlite3"
            ),
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }


# التحقق من قوة كلمات المرور
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": (
            "django.contrib.auth."
            "password_validation."
            "UserAttributeSimilarityValidator"
        ),
    },
    {
        "NAME": (
            "django.contrib.auth."
            "password_validation."
            "MinimumLengthValidator"
        ),
    },
    {
        "NAME": (
            "django.contrib.auth."
            "password_validation."
            "CommonPasswordValidator"
        ),
    },
    {
        "NAME": (
            "django.contrib.auth."
            "password_validation."
            "NumericPasswordValidator"
        ),
    },
]


# اللغة والتوقيت
LANGUAGE_CODE = "ar"
TIME_ZONE = "Asia/Riyadh"
USE_I18N = True
USE_TZ = True


# الملفات الثابتة
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

# توافق django-cloudinary-storage مع Django 6.1

# ملفات الطالبات المرفوعة
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"


# إعداد التخزين
CLOUDINARY_URL = os.environ.get(
    "CLOUDINARY_URL",
    "",
).strip()

STORAGES = {
    "staticfiles": {
        "BACKEND": (
            "whitenoise.storage."
            "CompressedManifestStaticFilesStorage"
        ),
    },
}

if CLOUDINARY_URL:
    STORAGES["default"] = {
        "BACKEND": (
            "cloudinary_storage.storage."
            "MediaCloudinaryStorage"
        ),
    }
else:
    if not DEBUG:
        raise ImproperlyConfigured(
            "يجب تعريف CLOUDINARY_URL في بيئة الإنتاج."
        )

    STORAGES["default"] = {
        "BACKEND": (
            "django.core.files.storage."
            "FileSystemStorage"
        ),
    }


# نوع المفتاح الأساسي
DEFAULT_AUTO_FIELD = (
    "django.db.models.BigAutoField"
)


# إعدادات البريد الحالية
EMAIL_BACKEND = (
    "django.core.mail.backends."
    "console.EmailBackend"
)


# إعدادات تسجيل الدخول والخروج
LOGIN_URL = "accounts:login"
LOGIN_REDIRECT_URL = "accounts:dashboard"
LOGOUT_REDIRECT_URL = "accounts:home"


# حماية الملفات المرفوعة
FILE_UPLOAD_PERMISSIONS = 0o640


# إعدادات الأمان الخاصة بالإنتاج
if not DEBUG:
    SECURE_PROXY_SSL_HEADER = (
        "HTTP_X_FORWARDED_PROTO",
        "https",
    )

    SECURE_SSL_REDIRECT = True

    # نبدأ بساعة واحدة، ثم نرفعها بعد نجاح النشر
    SECURE_HSTS_SECONDS = int(
        os.environ.get(
            "SECURE_HSTS_SECONDS",
            "3600",
        )
    )

    SECURE_HSTS_INCLUDE_SUBDOMAINS = False
    SECURE_HSTS_PRELOAD = False

    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"

    CSRF_COOKIE_SECURE = True
    CSRF_COOKIE_SAMESITE = "Lax"

    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_REFERRER_POLICY = (
        "strict-origin-when-cross-origin"
    )

    X_FRAME_OPTIONS = "DENY"


# تسجيل أخطاء الإنتاج في سجلات Render
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": (
                "logging.StreamHandler"
            ),
        },
    },
    "root": {
        "handlers": ["console"],
        "level": os.environ.get(
            "LOG_LEVEL",
            "INFO",
        ),
    },
}