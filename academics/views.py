from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_GET

from .models import Classroom, Enrollment, TeachingAssignment


def ensure_teacher_permission(user):
    """التأكد من أن المستخدم معلمة أو مديرة نظام."""

    if user.is_superuser:
        return

    if user.role != "teacher":
        raise PermissionDenied(
            "ليس لديك صلاحية للوصول إلى بيانات الصفوف."
        )


@login_required
@require_GET
def teacher_classrooms(request):
    """عرض الشعب والمقررات المسندة إلى المعلمة."""

    ensure_teacher_permission(request.user)

    assignments = TeachingAssignment.objects.filter(
        is_active=True,
        classroom__is_active=True,
    )

    if not request.user.is_superuser:
        assignments = assignments.filter(
            teacher=request.user,
        )

    assignments = assignments.select_related(
        "teacher",
        "subject",
        "classroom",
        "classroom__school",
        "classroom__academic_year",
        "classroom__grade_level",
    ).order_by(
        "classroom__grade_level__order",
        "classroom__name",
        "subject__name",
    )

    context = {
        "page_title": "صفوفي وشعبي",
        "assignments": assignments,
    }

    return render(
        request,
        "academics/teacher_classrooms.html",
        context,
    )


@login_required
@require_GET
def classroom_detail(request, classroom_id):
    """عرض تفاصيل الشعبة والطالبات المسجلات فيها."""

    ensure_teacher_permission(request.user)

    classroom = get_object_or_404(
        Classroom.objects.select_related(
            "school",
            "academic_year",
            "grade_level",
            "homeroom_teacher",
        ),
        pk=classroom_id,
        is_active=True,
    )

    if not request.user.is_superuser:
        has_permission = TeachingAssignment.objects.filter(
            teacher=request.user,
            classroom=classroom,
            is_active=True,
        ).exists()

        if not has_permission:
            raise PermissionDenied(
                "هذه الشعبة غير مسندة إلى حسابك."
            )

    enrollments = Enrollment.objects.filter(
        classroom=classroom,
        status=Enrollment.Status.ACTIVE,
    ).select_related(
        "student",
    ).order_by(
        "student__first_name",
        "student__last_name",
        "student__username",
    )

    teaching_assignments = (
        TeachingAssignment.objects.filter(
            classroom=classroom,
            is_active=True,
        )
        .select_related(
            "teacher",
            "subject",
        )
        .order_by("subject__name")
    )

    context = {
        "page_title": f"الشعبة {classroom}",
        "classroom": classroom,
        "enrollments": enrollments,
        "teaching_assignments": teaching_assignments,
    }

    return render(
        request,
        "academics/classroom_detail.html",
        context,
    )