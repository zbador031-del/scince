from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path


urlpatterns = [
    # لوحة إدارة Django
    path("admin/", admin.site.urls),

    # الصفحة الرئيسية والحسابات
    path("", include("accounts.urls")),

    # الإدارة الأكاديمية
    path("academics/", include("academics.urls")),

    # الأنشطة التعليمية
    path("activities/", include("activities.urls")),

    # دفاتر الطالبات والأعمال
    path("portfolios/", include("portfolios.urls")),

    # التقييم والتغذية الراجعة
    path("assessment/", include("assessment.urls")),

    # أدوات الذكاء الاصطناعي
    path("intelligence/", include("intelligence.urls")),
]


# عرض الملفات المرفوعة محليًا أثناء التطوير فقط
if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT,
    )