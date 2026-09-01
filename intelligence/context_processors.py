import logging

from django.core.cache import cache
from django.db import DatabaseError
from django.db.models import Q
from django.utils import timezone

from portfolios.models import Submission

from .models import MonthlyHonor
from .services.monthly_honor import generate_monthly_honor


logger = logging.getLogger(__name__)


def monthly_honor_ticker(request):
    """
    احتساب عالمة الشهر تلقائيًا وإتاحتها لجميع صفحات الموقع.

    يعاد فحص النتائج كل ساعة، لتحديث الشريط عند إضافة
    تقييمات جديدة دون تنفيذ أوامر يدوية.
    """

    today = timezone.localdate()

    cache_key = (
        f"monthly_honor_calculation_{today.isoformat()}"
    )

    featured_student_names = []

    try:
        if cache.get(cache_key) is None:
            generate_monthly_honor(target_date=today)

            cache.set(
                cache_key,
                True,
                timeout=60 * 60,
            )

        monthly_honor = (
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
            .order_by(
                "-month_start",
                "-average_score",
            )
            .first()
        )

        featured_submissions = (
            Submission.objects.filter(
                Q(is_featured=True)
                | Q(status=Submission.Status.FEATURED)
            )
            .select_related("portfolio__student")
            .prefetch_related("collaborators")
            .order_by(
                "-updated_at",
                "pk",
            )
        )

        for submission in featured_submissions:
            students = [submission.portfolio.student]
            students.extend(submission.collaborators.all())

            # يظهر الاسم مرة عن كل عمل متميز؛ فإذا تميز للطالبة
            # أكثر من عمل يظهر اسمها بعدد تلك الأعمال.
            for student in students:
                featured_student_names.append(
                    student.get_full_name().strip()
                    or student.username
                )

    except DatabaseError:
        logger.exception(
            "تعذر احتساب أو تحميل عالمة الشهر."
        )

        monthly_honor = None

    return {
        "monthly_honor_ticker": monthly_honor,
        "featured_student_names": featured_student_names,
    }
