import calendar
from collections import defaultdict
from datetime import date, timedelta
from decimal import Decimal

from django.db import transaction
from django.db.models import Q
from django.utils import timezone
from hijridate import Gregorian

from assessment.models import Evaluation
from portfolios.models import Submission

from ..models import MonthlyHonor


HIJRI_MONTHS = {
    1: "محرم",
    2: "صفر",
    3: "ربيع الأول",
    4: "ربيع الآخر",
    5: "جمادى الأولى",
    6: "جمادى الآخرة",
    7: "رجب",
    8: "شعبان",
    9: "رمضان",
    10: "شوال",
    11: "ذو القعدة",
    12: "ذو الحجة",
}


def get_month_range(target_date=None):
    """إرجاع أول وآخر يوم من الشهر الميلادي المحدد."""

    target_date = target_date or timezone.localdate()

    month_start = target_date.replace(day=1)

    last_day = calendar.monthrange(
        target_date.year,
        target_date.month,
    )[1]

    month_end = target_date.replace(day=last_day)

    return month_start, month_end


def get_previous_month_range(month_start):
    """إرجاع أول وآخر يوم من الشهر السابق."""

    previous_month_end = month_start - timedelta(days=1)
    previous_month_start = previous_month_end.replace(day=1)

    return previous_month_start, previous_month_end


def get_hijri_month_label(month_end):
    """إنشاء اسم الشهر الهجري العربي."""

    hijri_date = Gregorian.fromdate(month_end).to_hijri()
    month_name = HIJRI_MONTHS[hijri_date.month]

    return f"{month_name} {hijri_date.year}هـ"


def normalize_evaluation_score(evaluation):
    """تحويل درجة التقييم إلى درجة موحدة من 20."""

    if evaluation.total_score is None:
        return None

    maximum_score = sum(
        (
            criterion.max_points
            for criterion in evaluation.rubric.criteria.all()
        ),
        Decimal("0"),
    )

    if maximum_score <= 0:
        return min(
            Decimal("20"),
            Decimal(evaluation.total_score),
        )

    normalized_score = (
        Decimal(evaluation.total_score)
        / maximum_score
        * Decimal("20")
    )

    return min(
        Decimal("20"),
        max(Decimal("0"), normalized_score),
    )


def get_student_average(student_id, date_start, date_end):
    """حساب متوسط تقييمات طالبة خلال مدة محددة."""

    evaluations = (
        Evaluation.objects.filter(
            status=Evaluation.Status.PUBLISHED,
            total_score__isnull=False,
            evaluated_at__date__range=(
                date_start,
                date_end,
            ),
            submission_version__is_current=True,
            submission_version__submission__portfolio__student_id=(
                student_id
            ),
        )
        .select_related(
            "rubric",
            "submission_version",
            "submission_version__submission",
            "submission_version__submission__portfolio",
        )
        .prefetch_related("rubric__criteria")
    )

    scores = []

    for evaluation in evaluations:
        score = normalize_evaluation_score(evaluation)

        if score is not None:
            scores.append(score)

    if not scores:
        return None

    return sum(scores, Decimal("0")) / Decimal(len(scores))


def get_month_evaluations(month_start, month_end):
    """جلب التقييمات المنشورة والحالية خلال الشهر."""

    return (
        Evaluation.objects.filter(
            status=Evaluation.Status.PUBLISHED,
            total_score__isnull=False,
            evaluated_at__date__range=(
                month_start,
                month_end,
            ),
            submission_version__is_current=True,
        )
        .select_related(
            "rubric",
            "submission_version",
            "submission_version__submission",
            "submission_version__submission__portfolio",
            "submission_version__submission__portfolio__student",
            "submission_version__submission__portfolio__classroom",
        )
        .prefetch_related("rubric__criteria")
    )


def build_student_candidates(month_start, month_end):
    """بناء مؤشرات الطالبات المرشحات تلقائيًا."""

    student_scores = defaultdict(list)
    student_data = {}

    evaluations = get_month_evaluations(
        month_start,
        month_end,
    )

    for evaluation in evaluations:
        portfolio = (
            evaluation
            .submission_version
            .submission
            .portfolio
        )

        score = normalize_evaluation_score(evaluation)

        if score is None:
            continue

        student_id = portfolio.student_id

        student_scores[student_id].append(score)

        student_data[student_id] = {
            "student": portfolio.student,
            "classroom": portfolio.classroom,
        }

    previous_start, previous_end = get_previous_month_range(
        month_start
    )

    candidates = []

    for student_id, scores in student_scores.items():
        student = student_data[student_id]["student"]
        classroom = student_data[student_id]["classroom"]

        average_score = (
            sum(scores, Decimal("0"))
            / Decimal(len(scores))
        )

        submissions = Submission.objects.filter(
            portfolio__student_id=student_id,
            submitted_at__date__range=(
                month_start,
                month_end,
            ),
        )

        submitted_count = submissions.count()

        approved_submissions = submissions.filter(
            Q(
                status__in=[
                    Submission.Status.APPROVED,
                    Submission.Status.FEATURED,
                ]
            )
            | Q(is_featured=True)
        ).distinct()

        approved_count = approved_submissions.count()

        featured_submissions = submissions.filter(
            Q(status=Submission.Status.FEATURED)
            | Q(is_featured=True)
        ).distinct()

        featured_count = featured_submissions.count()

        if submitted_count:
            completion_rate = (
                Decimal(approved_count)
                / Decimal(submitted_count)
                * Decimal("100")
            )
        else:
            completion_rate = Decimal("0")

        previous_average = get_student_average(
            student_id,
            previous_start,
            previous_end,
        )

        if previous_average is None:
            improvement_rate = Decimal("0")
        else:
            improvement_rate = (
                (average_score - previous_average)
                / Decimal("20")
                * Decimal("100")
            )

        average_percentage = (
            average_score
            / Decimal("20")
            * Decimal("100")
        )

        positive_improvement = max(
            Decimal("0"),
            improvement_rate,
        )

        featured_bonus = min(
            Decimal("5"),
            Decimal(featured_count) * Decimal("2.5"),
        )

        ranking_score = (
            average_percentage * Decimal("0.65")
            + completion_rate * Decimal("0.20")
            + positive_improvement * Decimal("0.10")
            + featured_bonus
        )

        featured_submission = (
            featured_submissions
            .order_by("-submitted_at")
            .first()
        )

        candidates.append(
            {
                "student": student,
                "classroom": classroom,
                "average_score": average_score,
                "completion_rate": completion_rate,
                "improvement_rate": improvement_rate,
                "submitted_count": submitted_count,
                "approved_count": approved_count,
                "featured_count": featured_count,
                "featured_submission": featured_submission,
                "ranking_score": ranking_score,
            }
        )

    return candidates


@transaction.atomic
def generate_monthly_honor(target_date=None):
    """اختيار عالمة الشهر وتحديث الشريط تلقائيًا."""

    target_date = target_date or timezone.localdate()

    if not isinstance(target_date, date):
        raise TypeError(
            "يجب أن يكون التاريخ من النوع date."
        )

    month_start, month_end = get_month_range(target_date)

    candidates = build_student_candidates(
        month_start,
        month_end,
    )

    if not candidates:
        return None

    winner = max(
        candidates,
        key=lambda candidate: (
            candidate["ranking_score"],
            candidate["average_score"],
            candidate["completion_rate"],
            candidate["featured_count"],
        ),
    )

    student = winner["student"]
    classroom = winner["classroom"]

    student_name = (
        student.first_name.strip()
        if student.first_name
        else student.username
    )

    ticker_message = (
        f"نبارك للطالبة {student_name} من فصل "
        f"{classroom} حصولها على لقب عالمة الشهر، "
        f"بمتوسط {winner['average_score']:.2f} من 20."
    )

    selection_reason = (
        f"تم الاختيار تلقائيًا بناءً على متوسط التقييم "
        f"({winner['average_score']:.2f} من 20)، "
        f"ونسبة الإنجاز "
        f"({winner['completion_rate']:.2f}٪)، "
        f"ونسبة التحسن "
        f"({winner['improvement_rate']:.2f}٪)، "
        f"وعدد الأعمال المميزة "
        f"({winner['featured_count']})."
    )

    honor, _created = MonthlyHonor.objects.update_or_create(
        month_start=month_start,
        defaults={
            "student": student,
            "classroom": classroom,
            "month_end": month_end,
            "hijri_month_label": get_hijri_month_label(
                month_end
            ),
            "average_score": round(
                winner["average_score"],
                2,
            ),
            "completion_rate": round(
                winner["completion_rate"],
                2,
            ),
            "improvement_rate": round(
                winner["improvement_rate"],
                2,
            ),
            "submitted_activities": (
                winner["submitted_count"]
            ),
            "approved_activities": (
                winner["approved_count"]
            ),
            "featured_activities": (
                winner["featured_count"]
            ),
            "featured_submission": (
                winner["featured_submission"]
            ),
            "selection_reason": selection_reason,
            "ticker_message": ticker_message,
            "publish_student_name": True,
            "is_approved": True,
            "is_active_in_ticker": True,
            "approved_by": None,
            "approved_at": timezone.now(),
        },
    )

    MonthlyHonor.objects.exclude(
        pk=honor.pk,
    ).update(
        is_active_in_ticker=False,
    )

    return honor