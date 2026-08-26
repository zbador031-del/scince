from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, render

from .models import MonthlyHonor


def user_can_view_monthly_reports(user):
    """السماح للمعلمة أو مديرة النظام بعرض التقارير."""

    return (
        user.is_authenticated
        and (
            user.is_staff
            or getattr(user, "role", "") == "teacher"
        )
    )


@login_required
def monthly_honor_archive(request):
    """عرض أرشيف عالمة الشهر."""

    if not user_can_view_monthly_reports(request.user):
        raise PermissionDenied(
            "ليس لديك صلاحية لعرض التقارير الشهرية."
        )

    monthly_honors = (
        MonthlyHonor.objects.select_related(
            "student",
            "classroom",
            "classroom__grade_level",
            "featured_submission",
        )
        .filter(is_approved=True)
        .order_by("-month_start")
    )

    context = {
        "monthly_honors": monthly_honors,
    }

    return render(
        request,
        "intelligence/monthly_honor_archive.html",
        context,
    )


@login_required
def monthly_honor_report(request, honor_id):
    """عرض التقرير التفصيلي لعالمة الشهر."""

    if not user_can_view_monthly_reports(request.user):
        raise PermissionDenied(
            "ليس لديك صلاحية لعرض هذا التقرير."
        )

    monthly_honor = get_object_or_404(
        MonthlyHonor.objects.select_related(
            "student",
            "classroom",
            "classroom__grade_level",
            "featured_submission",
            "approved_by",
        ),
        pk=honor_id,
        is_approved=True,
    )

    context = {
        "monthly_honor": monthly_honor,
    }

    return render(
        request,
        "intelligence/monthly_honor_report.html",
        context,
    )