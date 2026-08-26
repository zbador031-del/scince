from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db.models import Avg, Count, Q
from django.shortcuts import render
from django.views.decorators.http import require_GET

from academics.models import (
    Classroom,
    Enrollment,
    TeachingAssignment,
)
from assessment.models import Evaluation
from portfolios.models import Submission


def _ensure_teacher(user):
    """السماح للمعلمة أو مديرة النظام فقط."""

    if user.is_superuser:
        return

    if getattr(user, "role", None) != "teacher":
        raise PermissionDenied(
            "هذه الصفحة مخصصة للمعلمات فقط."
        )


def _teacher_classroom_ids(user):
    """الشعب التي يحق للمعلمة الاطلاع عليها."""

    if user.is_superuser:
        return Classroom.objects.filter(
            is_active=True
        ).values_list(
            "id",
            flat=True,
        )

    return TeachingAssignment.objects.filter(
        teacher=user,
        is_active=True,
        classroom__is_active=True,
    ).values_list(
        "classroom_id",
        flat=True,
    )


@login_required
@require_GET
def teacher_analytics(request):
    """لوحة مؤشرات وتحليلات أداء الطالبات."""

    _ensure_teacher(request.user)

    classroom_ids = list(
        _teacher_classroom_ids(request.user)
    )

    # قراءة الفلاتر من رابط الصفحة
    selected_classroom = request.GET.get(
        "classroom",
        "",
    ).strip()

    selected_status = request.GET.get(
        "status",
        "",
    ).strip()

    valid_statuses = {
        value
        for value, _ in Submission.Status.choices
    }

    # التحقق من أن الفصل تابع للمعلمة
    filtered_classroom_ids = classroom_ids

    if (
        selected_classroom.isdigit()
        and int(selected_classroom) in classroom_ids
    ):
        filtered_classroom_ids = [
            int(selected_classroom)
        ]
    else:
        selected_classroom = ""

    # التحقق من صحة حالة العمل
    if selected_status not in valid_statuses:
        selected_status = ""

    # جميع فصول المعلمة لعرضها في قائمة الفلترة
    filter_classrooms = Classroom.objects.filter(
        id__in=classroom_ids
    ).select_related(
        "grade_level",
        "academic_year",
    ).order_by(
        "grade_level__order",
        "name",
    )

    # الأعمال التي تدخل في التحليل
    submissions = Submission.objects.filter(
        portfolio__classroom_id__in=(
            filtered_classroom_ids
        ),
        portfolio__is_active=True,
    )

    # تطبيق فلتر حالة العمل
    if selected_status:
        submissions = submissions.filter(
            status=selected_status
        )

    evaluations = Evaluation.objects.filter(
        submission_version__submission__in=(
            submissions
        )
    ).exclude(
        status=Evaluation.Status.DRAFT
    )

    total_students = (
        Enrollment.objects.filter(
            classroom_id__in=(
                filtered_classroom_ids
            ),
            status=Enrollment.Status.ACTIVE,
        )
        .values("student_id")
        .distinct()
        .count()
    )

    students_with_work = (
        submissions.values(
            "portfolio__student_id"
        )
        .distinct()
        .count()
    )

    total_submissions = submissions.count()

    evaluated_submissions = (
        evaluations.values(
            "submission_version__submission_id"
        )
        .distinct()
        .count()
    )

    pending_submissions = submissions.filter(
        status__in=[
            Submission.Status.SUBMITTED,
            Submission.Status.RESUBMITTED,
            Submission.Status.UNDER_REVIEW,
        ]
    ).count()

    approved_submissions = submissions.filter(
        status__in=[
            Submission.Status.APPROVED,
            Submission.Status.FEATURED,
        ]
    ).count()

    revision_submissions = submissions.filter(
        status=Submission.Status.REVISION_REQUIRED
    ).count()

    featured_submissions = submissions.filter(
        Q(status=Submission.Status.FEATURED)
        | Q(is_featured=True)
    ).distinct().count()

    average_score_value = evaluations.aggregate(
        average=Avg("total_score")
    )["average"]

    average_score = (
        round(float(average_score_value), 2)
        if average_score_value is not None
        else 0
    )

    completion_rate = (
        round(
            (
                students_with_work
                / total_students
            )
            * 100,
            1,
        )
        if total_students
        else 0
    )

    evaluation_rate = (
        round(
            (
                evaluated_submissions
                / total_submissions
            )
            * 100,
            1,
        )
        if total_submissions
        else 0
    )

    status_counts = {
        item["status"]: item["count"]
        for item in submissions.values(
            "status"
        ).annotate(
            count=Count("id")
        )
    }

    status_analytics = []

    for value, label in Submission.Status.choices:
        count = status_counts.get(value, 0)

        percentage = (
            round(
                (
                    count
                    / total_submissions
                )
                * 100,
                1,
            )
            if total_submissions
            else 0
        )

        status_analytics.append(
            {
                "value": value,
                "label": label,
                "count": count,
                "percentage": percentage,
            }
        )

    # الفصول التي تدخل في المقارنة
    classrooms = filter_classrooms.filter(
        id__in=filtered_classroom_ids
    )

    classroom_analytics = []

    for classroom in classrooms:
        classroom_students = (
            Enrollment.objects.filter(
                classroom=classroom,
                status=Enrollment.Status.ACTIVE,
            )
            .values("student_id")
            .distinct()
            .count()
        )

        classroom_submissions = submissions.filter(
            portfolio__classroom=classroom
        )

        classroom_students_with_work = (
            classroom_submissions.values(
                "portfolio__student_id"
            )
            .distinct()
            .count()
        )

        classroom_submission_count = (
            classroom_submissions.count()
        )

        classroom_evaluations = evaluations.filter(
            submission_version__submission__in=(
                classroom_submissions
            )
        )

        classroom_evaluated_count = (
            classroom_evaluations.values(
                "submission_version__submission_id"
            )
            .distinct()
            .count()
        )

        classroom_average_value = (
            classroom_evaluations.aggregate(
                average=Avg("total_score")
            )["average"]
        )

        classroom_completion = (
            round(
                (
                    classroom_students_with_work
                    / classroom_students
                )
                * 100,
                1,
            )
            if classroom_students
            else 0
        )

        classroom_evaluation_rate = (
            round(
                (
                    classroom_evaluated_count
                    / classroom_submission_count
                )
                * 100,
                1,
            )
            if classroom_submission_count
            else 0
        )

        classroom_average = (
            round(
                float(classroom_average_value),
                2,
            )
            if classroom_average_value is not None
            else 0
        )

        classroom_analytics.append(
            {
                "classroom": classroom,
                "student_count": classroom_students,
                "students_with_work": (
                    classroom_students_with_work
                ),
                "submission_count": (
                    classroom_submission_count
                ),
                "evaluated_count": (
                    classroom_evaluated_count
                ),
                "completion_rate": (
                    classroom_completion
                ),
                "evaluation_rate": (
                    classroom_evaluation_rate
                ),
                "average_score": classroom_average,
            }
        )

    recent_submissions = (
        submissions.select_related(
            "portfolio",
            "portfolio__student",
            "portfolio__classroom",
        )
        .order_by("-created_at")[:8]
    )

    context = {
        "total_students": total_students,
        "students_with_work": students_with_work,
        "total_submissions": total_submissions,
        "evaluated_submissions": (
            evaluated_submissions
        ),
        "pending_submissions": (
            pending_submissions
        ),
        "approved_submissions": (
            approved_submissions
        ),
        "revision_submissions": (
            revision_submissions
        ),
        "featured_submissions": (
            featured_submissions
        ),
        "average_score": average_score,
        "completion_rate": completion_rate,
        "evaluation_rate": evaluation_rate,
        "status_analytics": status_analytics,
        "classroom_analytics": classroom_analytics,
        "recent_submissions": recent_submissions,

        # بيانات الفلاتر
        "filter_classrooms": filter_classrooms,
        "status_choices": Submission.Status.choices,
        "selected_classroom": selected_classroom,
        "selected_status": selected_status,
        "filters_active": bool(
            selected_classroom
            or selected_status
        ),
    }

    return render(
        request,
        "intelligence/teacher_analytics.html",
        context,
    )