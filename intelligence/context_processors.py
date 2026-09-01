import logging

from django.core.cache import cache
from django.db.models import Q
from django.utils import timezone

from portfolios.models import Submission

from .models import MonthlyHonor
from .services.monthly_honor import generate_monthly_honor


logger = logging.getLogger(__name__)


def _get_monthly_honor(today):
    cache_key = f"monthly_honor_calculation_{today.isoformat()}"

    if cache.get(cache_key) is None:
        generate_monthly_honor(target_date=today)
        cache.set(cache_key, True, timeout=60 * 60)

    return (
        MonthlyHonor.objects.select_related(
            "student",
            "classroom",
            "classroom__grade_level",
        )
        .filter(
            is_approved=True,
            is_active_in_ticker=True,
            month_start__lte=today,
            month_end__gte=today,
        )
        .order_by("-month_start", "-average_score")
        .first()
    )


def _get_featured_student_names():
    featured_submissions = (
        Submission.objects.filter(
            Q(is_featured=True)
            | Q(status=Submission.Status.FEATURED)
        )
        .select_related("portfolio__student")
        .prefetch_related("collaborators")
        .order_by("-updated_at", "pk")
    )

    names = []
    seen_student_ids = set()

    for submission in featured_submissions:
        students = [submission.portfolio.student]
        students.extend(submission.collaborators.all())

        for student in students:
            if student.pk in seen_student_ids:
                continue

            seen_student_ids.add(student.pk)
            names.append(
                student.get_full_name().strip()
                or student.username
            )

    return names


def monthly_honor_ticker(request):
    """إتاحة بيانات الشريط دون السماح له بتعطيل صفحات الموقع."""

    monthly_honor = None
    featured_student_names = []

    try:
        monthly_honor = _get_monthly_honor(timezone.localdate())
    except Exception:
        logger.exception("تعذر تحميل عالمة الشهر؛ استمر عرض الصفحة.")

    try:
        featured_student_names = _get_featured_student_names()
    except Exception:
        logger.exception("تعذر تحميل شريط التميز؛ استمر عرض الصفحة.")

    return {
        "monthly_honor_ticker": monthly_honor,
        "featured_student_names": featured_student_names,
    }
