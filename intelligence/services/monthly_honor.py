import calendar
from collections import defaultdict
from datetime import date, timedelta
from decimal import Decimal

from django.db import transaction
from django.db.models import Q
from django.utils import timezone
from hijridate import Gregorian

from assessment.models import Evaluation
from intelligence.models import MonthlyHonor
from portfolios.models import Submission


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
    """إرجاع أول وآخر يوم من الشهر."""

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

    previous_end = month_start - timedelta(days=1)
    previous_start = previous_end.replace(day=1)

    return previous_start, previous_end


def get_hijri_month_label(month_end):
    """إنشاء اسم الشهر الهجري العربي."""

    hijri_date = Gregorian.fromdate(month_end).to_hijri()
    month_name = HIJRI_MONTHS[hijri_date.month]

    return f"{month_name} {hijri_date.year}هـ"


def normalize_score(evaluation):
    """تحويل التقييم إلى درجة موحدة من 20."""

    if evaluation.total_score is None:
        return None

    maximum_score = sum(
        (
            criterion.max_points
            for criterion in evaluation.rubric.criteria.all()
        ),
        Decimal("0"),
    )

    total_score = Decimal(evaluation.total_score)

    if maximum_score <= 0:
        return min(
            Decimal("20"),
            max(Decimal("0"), total_score),
        )

    score = (
        total_score
        / maximum_score
        * Decimal("20")
    )

    return min(
        Decimal("20"),
        max(Decimal("0"), score),
    )


def get_evaluations(date_start, date_end, student_id=None):
    """جلب التقييمات المنشورة فقط."""

    evaluations = Evaluation.objects.filter(
        status=Evaluation.Status.PUBLISHED,
        total_score__isnull=False,
        evaluated_at__date__range=(
            date_start,
            date_end,
        ),
        submission_version__is_current=True,
    )

    if student_id is not None:
        evaluations = evaluations.filter(
            submission_version__submission__portfolio__student_id=(
                student_id
            )
        )

    return (
        evaluations
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


def get_student_average(student_id, date_start, date_end):
    """حساب متوسط طالبة خلال مدة محددة."""

    scores = []

    for evaluation in get_evaluations(
        date_start,
        date_end,
        student_id=student_id,
    ):
        score = normalize_score(evaluation)

        if score is not None:
            scores.append(score)

    if not scores:
        return None

    return (
        sum(scores, Decimal("0"))
        / Decimal(len(scores))
    )


def build_candidates(month_start, month_end):
    """حساب مؤشرات الطالبات المرشحات."""

    scores_by_student = defaultdict(list)
    student_information = {}

    for evaluation in get_evaluations(
        month_start,
        month_end,
    ):
        portfolio = (
            evaluation
            .submission_version
            .submission
            .portfolio
        )

        score = normalize_score(evaluation)

        if score is None:
            continue

        student_id = portfolio.student_id

        scores_by_student[student_id].append(score)

        student_information[student_id] = {
            "student": portfolio.student,
            "classroom": portfolio.classroom,
        }

    previous_start, previous_end = (
        get_previous_month_range(month_start)
    )

    candidates = []

    for student_id, scores in scores_by_student.items():
        information = student_information[student_id]

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

        if submitted_count > 0:
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
                "student": information["student"],
                "classroom": information["classroom"],
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
    """اختيار عالمة الشهر وتشغيل الشريط تلقائيًا."""

    target_date = target_date or timezone.localdate()

    if not isinstance(target_date, date):
        raise TypeError("يجب إدخال تاريخ صحيح.")

    month_start, month_end = get_month_range(target_date)

    candidates = build_candidates(
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
        f"اختيار تلقائي بمتوسط "
        f"{winner['average_score']:.2f} من 20، "
        f"ونسبة إنجاز "
        f"{winner['completion_rate']:.2f}٪، "
        f"ونسبة تحسن "
        f"{winner['improvement_rate']:.2f}٪، "
        f"وعدد أعمال مميزة "
        f"{winner['featured_count']}."
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