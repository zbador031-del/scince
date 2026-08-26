import logging

from django.core.cache import cache
from django.db import DatabaseError
from django.utils import timezone

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

    except DatabaseError:
        logger.exception(
            "تعذر احتساب أو تحميل عالمة الشهر."
        )

        monthly_honor = None

    return {
        "monthly_honor_ticker": monthly_honor,
    }