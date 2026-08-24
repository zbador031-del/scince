from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect, render
from django.views.decorators.http import require_GET

from .models import User


@require_GET
def home(request):
    """الصفحة الرئيسية العامة لجميع المستخدمين."""

    return render(request, "accounts/home.html")


@require_GET
def parent_inquiry(request):
    """الانتقال إلى منصة استعلام ولي الأمر."""

    inquiry_url = settings.PARENT_INQUIRY_URL

    if not inquiry_url.startswith("https://"):
        return redirect("accounts:home")

    return redirect(inquiry_url)


@login_required
@require_GET
def dashboard_redirect(request):
    """توجيه المستخدم إلى لوحته حسب نوع الحساب."""

    user = request.user

    if user.is_superuser or user.role == User.Role.ADMIN:
        return redirect("admin:index")

    if user.role == User.Role.TEACHER:
        return redirect("accounts:teacher_dashboard")

    if user.role == User.Role.STUDENT:
        return redirect("accounts:student_dashboard")

    if user.role == User.Role.PARENT:
        return redirect("accounts:parent_dashboard")

    return redirect("accounts:home")


@login_required
@require_GET
def teacher_dashboard(request):
    """لوحة المعلمة."""

    if (
        request.user.role != User.Role.TEACHER
        and not request.user.is_superuser
    ):
        raise PermissionDenied(
            "ليس لديك صلاحية لدخول لوحة المعلمة."
        )

    context = {
        "page_title": "لوحة المعلمة",
        "user": request.user,
    }

    return render(
        request,
        "accounts/teacher_dashboard.html",
        context,
    )


@login_required
@require_GET
def student_dashboard(request):
    """لوحة الطالبة."""

    if (
        request.user.role != User.Role.STUDENT
        and not request.user.is_superuser
    ):
        raise PermissionDenied(
            "ليس لديك صلاحية لدخول لوحة الطالبة."
        )

    context = {
        "page_title": "دفتر العلوم الخاص بي",
        "user": request.user,
    }

    return render(
        request,
        "accounts/student_dashboard.html",
        context,
    )


@login_required
@require_GET
def parent_dashboard(request):
    """لوحة ولي الأمر."""

    if (
        request.user.role != User.Role.PARENT
        and not request.user.is_superuser
    ):
        raise PermissionDenied(
            "ليس لديك صلاحية لدخول لوحة ولي الأمر."
        )

    context = {
        "page_title": "متابعة الطالبة",
        "user": request.user,
    }

    return render(
        request,
        "accounts/parent_dashboard.html",
        context,
    )