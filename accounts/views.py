from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect, render
from django.views.decorators.http import require_GET

from .models import User


@require_GET
def home(request):
    """عرض الصفحة الرئيسية لجميع المستخدمين."""

    return render(
        request,
        "accounts/home.html",
    )


@require_GET
def parent_inquiry(request):
    """الانتقال إلى صفحة استعلام ولي الأمر الخارجية."""

    inquiry_url = settings.PARENT_INQUIRY_URL

    if not inquiry_url.startswith("https://"):
        return redirect("accounts:home")

    return redirect(inquiry_url)


@login_required
@require_GET
def dashboard_redirect(request):
    """توجيه المستخدم إلى لوحته حسب نوع حسابه."""

    user = request.user

    # حساب المدير يفتح لوحة المعلمة.
    # لوحة إدارة جانكو تبقى متاحة من رابط إدارة النظام.
    if user.is_superuser:
        return redirect("accounts:teacher_dashboard")

    if user.role == User.Role.ADMIN:
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
    """عرض لوحة المعلمة."""

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
    """عرض لوحة الطالبة."""

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
    """عرض لوحة ولي الأمر."""

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