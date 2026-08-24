"""
URL configuration for scince project.
"""

from django.contrib import admin
from django.urls import include, path


urlpatterns = [
    # لوحة إدارة Django
    path("admin/", admin.site.urls),

    # الصفحة الرئيسية والحسابات
    path("", include("accounts.urls")),

    # الهيكل الدراسي والصفوف
    path("academics/", include("academics.urls")),

    # الأنشطة والأعمال المطلوبة
    path("activities/", include("activities.urls")),

    # دفاتر الطالبات
    path("portfolios/", include("portfolios.urls")),

    # التقييم والتغذية الراجعة
    path("assessment/", include("assessment.urls")),

    # الذكاء الاصطناعي والتحليلات
    path("intelligence/", include("intelligence.urls")),
]