from django.contrib.auth import views as auth_views
from django.urls import path

from . import views


app_name = "accounts"


urlpatterns = [
    # الصفحة الرئيسية
    path(
        "",
        views.home,
        name="home",
    ),


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
            template_name="accounts/login.html",
            redirect_authenticated_user=True,
        ),
        name="login",
    ),

    # تسجيل الخروج
    path(
        "logout/",
        auth_views.LogoutView.as_view(),
        name="logout",
    ),

    # التوجيه حسب نوع الحساب
    path(
        "dashboard/",
        views.dashboard_redirect,
        name="dashboard",
    ),

    # لوحة المعلمة
    path(
        "teacher/",
        views.teacher_dashboard,
        name="teacher_dashboard",
    ),

    # لوحة الطالبة
    path(
        "student/",
        views.student_dashboard,
        name="student_dashboard",
    ),

    # لوحة ولي الأمر
    path(
        "parent/",
        views.parent_dashboard,
        name="parent_dashboard",
    ),
]