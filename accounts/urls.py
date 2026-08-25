from django.contrib.auth import views as auth_views
from django.urls import path, reverse_lazy

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

    # تسجيل الدخول
    path(
        "login/",
        auth_views.LoginView.as_view(
            template_name="accounts/login.html"
        ),
        name="login",
    ),

    # تسجيل الخروج
    path(
        "logout/",
        auth_views.LogoutView.as_view(),
        name="logout",
    ),

    # تغيير كلمة المرور
    path(
        "password/change/",
        auth_views.PasswordChangeView.as_view(
            template_name="accounts/password_change.html",
            success_url=reverse_lazy("accounts:dashboard"),
        ),
        name="password_change",
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