from django.contrib.auth import views as auth_views
from django.urls import path

from . import views


app_name = "accounts"


urlpatterns = [
    # الصفحة الرئيسية
    path("", views.home, name="home"),

    # استعلام ولي الأمر
    path(
        "parent-inquiry/",
        views.parent_inquiry,
        name="parent_inquiry",
    ),

    # تسجيل الدخول والخروج
    path(
        "login/",
        auth_views.LoginView.as_view(
            template_name="accounts/login.html"
        ),
        name="login",
    ),
    path(
        "logout/",
        auth_views.LogoutView.as_view(),
        name="logout",
    ),

    # توجيه المستخدم إلى لوحة التحكم المناسبة
    path(
        "dashboard/",
        views.dashboard_redirect,
        name="dashboard",
    ),

    # لوحات التحكم
    path(
        "teacher/dashboard/",
        views.teacher_dashboard,
        name="teacher_dashboard",
    ),
    path(
        "student/dashboard/",
        views.student_dashboard,
        name="student_dashboard",
    ),
    path(
        "parent/dashboard/",
        views.parent_dashboard,
        name="parent_dashboard",
    ),

    # إنشاء حسابات الطالبات دفعة واحدة
    path(
        "teacher/students/bulk-create/",
        views.bulk_create_students,
        name="bulk_create_students",
    ),
]