from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db.models import Avg, Count, Q
from django.http import Http404
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_GET

from assessment.models import CriterionScore, Evaluation
from portfolios.models import (
    Portfolio,
    Submission,
    SubmissionVersion,
)

from .views import (
    _ensure_teacher,
    _teacher_classroom_ids,
)


def _performance_level(percentage):
    """تحويل النسبة إلى مستوى أداء تربوي واضح."""

    if percentage >= 90:
        return "ممتاز"

    if percentage >= 80:
        return "متقدم"

    if percentage >= 70:
        return "متمكن"

    if percentage >= 60:
        return "نامٍ"

    return "يحتاج دعمًا"


def _trend_label(change_value):
    """وصف اتجاه تطور أداء الطالبة."""

    if change_value >= 5:
        return "تحسن ملحوظ"

    if change_value > 0:
        return "تحسن تدريجي"

    if change_value <= -5:
        return "انخفاض يحتاج متابعة"

    if change_value < 0:
        return "انخفاض طفيف"

    return "أداء مستقر"


@login_required
@require_GET
def student_analytics_report(
    request,
    portfolio_id,
):
    """التقرير التحليلي الفردي للطالبة."""



    portfolio = get_object_or_404(
        Portfolio.objects.select_related(
            "student",
            "classroom",
            "classroom__grade_level",
            "subject",
            "academic_year",
        ),
        pk=portfolio_id,
        is_active=True,
    )

    # الطالبة تستطيع مشاهدة تقريرها فقط
    is_student_owner = (
        getattr(request.user, "role", None) == "student"
        and portfolio.student_id == request.user.id
    )

    # غير الطالبة المالكة يجب أن تكون معلمة مخولة بهذا الفصل
    if not is_student_owner:
        _ensure_teacher(request.user)

        classroom_ids = set(
            _teacher_classroom_ids(request.user)
        )

        if portfolio.classroom_id not in classroom_ids:
            raise PermissionDenied(
                "لا تملكين صلاحية الاطلاع على تقرير هذه الطالبة."
            )
    submissions = (
        Submission.objects.filter(
            portfolio=portfolio
        )
        .select_related(
            "activity",
            "section",
        )
        .prefetch_related(
            "versions",
            "awarded_badges",
        )
    )

    evaluations = list(
        Evaluation.objects.filter(
            submission_version__submission__in=(
                submissions
            )
        )
        .exclude(
            status=Evaluation.Status.DRAFT
        )
        .select_related(
            "submission_version",
            "submission_version__submission",
            "rubric",
            "evaluator",
        )
        .prefetch_related(
            "rubric__criteria",
            "criterion_scores",
            "criterion_scores__criterion",
        )
        .order_by("-evaluated_at")
    )

    total_submissions = submissions.count()

    submitted_count = submissions.exclude(
        status=Submission.Status.DRAFT
    ).count()

    approved_count = submissions.filter(
        status__in=[
            Submission.Status.APPROVED,
            Submission.Status.FEATURED,
        ]
    ).count()

    revision_count = submissions.filter(
        status=Submission.Status.REVISION_REQUIRED
    ).count()

    featured_count = submissions.filter(
        Q(status=Submission.Status.FEATURED)
        | Q(is_featured=True)
    ).distinct().count()

    evaluated_submission_count = (
        Evaluation.objects.filter(
            submission_version__submission__in=(
                submissions
            )
        )
        .exclude(
            status=Evaluation.Status.DRAFT
        )
        .values(
            "submission_version__submission_id"
        )
        .distinct()
        .count()
    )

    evaluation_rate = (
        round(
            (
                evaluated_submission_count
                / total_submissions
            )
            * 100,
            1,
        )
        if total_submissions
        else 0
    )

    evaluation_rows = []

    for evaluation in evaluations:
        maximum_score = float(
            evaluation.rubric.maximum_score or 20
        )

        score = float(
            evaluation.total_score or 0
        )

        percentage = (
            round(
                (score / maximum_score) * 100,
                1,
            )
            if maximum_score
            else 0
        )

        evaluation_rows.append(
            {
                "evaluation": evaluation,
                "submission": (
                    evaluation
                    .submission_version
                    .submission
                ),
                "score": score,
                "maximum_score": maximum_score,
                "percentage": percentage,
                "performance_level": (
                    _performance_level(percentage)
                ),
            }
        )

    average_percentage = (
        round(
            sum(
                row["percentage"]
                for row in evaluation_rows
            )
            / len(evaluation_rows),
            1,
        )
        if evaluation_rows
        else 0
    )

    overall_level = _performance_level(
        average_percentage
    )

    latest_percentage = (
        evaluation_rows[0]["percentage"]
        if evaluation_rows
        else 0
    )

    earliest_percentage = (
        evaluation_rows[-1]["percentage"]
        if evaluation_rows
        else 0
    )

    performance_change = round(
        latest_percentage - earliest_percentage,
        1,
    )

    trend_label = _trend_label(
        performance_change
    )

    criterion_query = (
        CriterionScore.objects.filter(
            evaluation__in=evaluations
        )
        .values(
            "criterion__title",
            "criterion__max_points",
        )
        .annotate(
            average_score=Avg("score"),
            evaluation_count=Count("id"),
        )
        .order_by(
            "criterion__title"
        )
    )

    criterion_analytics = []

    for item in criterion_query:
        maximum_score = float(
            item["criterion__max_points"] or 0
        )

        average_score = float(
            item["average_score"] or 0
        )

        percentage = (
            round(
                (
                    average_score
                    / maximum_score
                )
                * 100,
                1,
            )
            if maximum_score
            else 0
        )

        criterion_analytics.append(
            {
                "title": item["criterion__title"],
                "average_score": round(
                    average_score,
                    2,
                ),
                "maximum_score": maximum_score,
                "percentage": percentage,
                "evaluation_count": (
                    item["evaluation_count"]
                ),
                "performance_level": (
                    _performance_level(percentage)
                ),
            }
        )

    strengths = [
        item
        for item in criterion_analytics
        if item["percentage"] >= 80
    ]

    support_needs = [
        item
        for item in criterion_analytics
        if item["percentage"] < 60
    ]
    learning_recommendation = (
    _learning_recommendation(
        average_percentage,
        support_needs,
    )
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

    ai_versions_count = (
        SubmissionVersion.objects.filter(
            submission__portfolio=portfolio,
            ai_used=True,
        )
        .distinct()
        .count()
    )

    badges = (
        portfolio.earned_badges.select_related(
            "badge",
            "submission",
            "awarded_by",
        )
        .order_by("-awarded_at")
    )

    latest_feedback = next(
        (
            row["evaluation"]
            for row in evaluation_rows
            if row["evaluation"].general_feedback
        ),
        None,
    )

    recent_submissions = (
        submissions.order_by("-created_at")[:8]
    )

    context = {
        "portfolio": portfolio,
        "student": portfolio.student,
        "classroom": portfolio.classroom,
        "total_submissions": total_submissions,
        "submitted_count": submitted_count,
        "approved_count": approved_count,
        "revision_count": revision_count,
        "featured_count": featured_count,
        "evaluated_submission_count": (
            evaluated_submission_count
        ),
        "evaluation_rate": evaluation_rate,
        "average_percentage": (
            average_percentage
        ),
        "overall_level": overall_level,
        "latest_percentage": (
            latest_percentage
        ),
        "performance_change": (
            performance_change
        ),
        "trend_label": trend_label,
        "evaluation_rows": evaluation_rows,
        "criterion_analytics": (
            criterion_analytics
        ),
        "strengths": strengths,
        "support_needs": support_needs,
                "learning_recommendation": (
            learning_recommendation
        ),
        "status_analytics": status_analytics,
        "ai_versions_count": (
            ai_versions_count
        ),
        "badges": badges,
        "latest_feedback": latest_feedback,
        "recent_submissions": (
            recent_submissions
        ),
    }

    return render(
        request,
        "intelligence/student_analytics_report.html",
        context,
    )

@login_required
@require_GET
def my_student_analytics_report(request):
    """عرض التقرير التحليلي للطالبة المسجلة حاليًا فقط."""

    if getattr(request.user, "role", None) != "student":
        raise PermissionDenied(
            "هذه الصفحة مخصصة للطالبات فقط."
        )

    portfolio = (
        Portfolio.objects.filter(
            student=request.user,
            is_active=True,
        )
        .order_by(
            "-academic_year__is_current",
            "-pk",
        )
        .first()
    )

    if portfolio is None:
        raise Http404(
            "لا يوجد دفتر علوم نشط مرتبط بحساب الطالبة."
        )

    return student_analytics_report(
        request,
        portfolio.pk,
    )


@login_required
@require_GET
def student_reports_list(request):
    """قائمة التقارير الفردية لجميع طالبات المعلمة."""

    _ensure_teacher(request.user)

    classroom_ids = list(
        _teacher_classroom_ids(request.user)
    )

    selected_classroom = request.GET.get(
        "classroom",
        "",
    ).strip()

    search_query = request.GET.get(
        "q",
        "",
    ).strip()

    classrooms = (
        Portfolio.objects.filter(
            classroom_id__in=classroom_ids,
            is_active=True,
        )
        .values(
            "classroom_id",
            "classroom__name",
            "classroom__grade_level__name",
            "classroom__grade_level__order",
        )
        .distinct()
        .order_by(
            "classroom__grade_level__order",
            "classroom__name",
        )
    )

    portfolios = (
        Portfolio.objects.filter(
            classroom_id__in=classroom_ids,
            is_active=True,
        )
        .select_related(
            "student",
            "classroom",
            "classroom__grade_level",
            "subject",
            "academic_year",
        )
        .annotate(
            submission_count=Count(
                "submissions",
                distinct=True,
            ),
            approved_count=Count(
                "submissions",
                filter=Q(
                    submissions__status__in=[
                        Submission.Status.APPROVED,
                        Submission.Status.FEATURED,
                    ]
                ),
                distinct=True,
            ),
            evaluation_count=Count(
                "submissions__versions__evaluation",
                filter=~Q(
                    submissions__versions__evaluation__status=(
                        Evaluation.Status.DRAFT
                    )
                ),
                distinct=True,
            ),
        )
    )

    if (
        selected_classroom.isdigit()
        and int(selected_classroom) in classroom_ids
    ):
        portfolios = portfolios.filter(
            classroom_id=int(selected_classroom)
        )
    else:
        selected_classroom = ""

    if search_query:
        portfolios = portfolios.filter(
            Q(
                student__first_name__icontains=(
                    search_query
                )
            )
            | Q(
                student__last_name__icontains=(
                    search_query
                )
            )
            | Q(
                student__username__icontains=(
                    search_query
                )
            )
        )

    portfolios = portfolios.order_by(
        "classroom__grade_level__order",
        "classroom__name",
        "student__first_name",
        "student__last_name",
        "student__username",
    )

    context = {
        "portfolios": portfolios,
        "classrooms": classrooms,
        "selected_classroom": (
            selected_classroom
        ),
        "search_query": search_query,
        "result_count": portfolios.count(),
    }

    return render(
        request,
        "intelligence/student_reports_list.html",
        context,
    )
def _learning_recommendation(
    percentage,
    support_needs,
):
    """توليد توصية تعليمية وفق مستوى أداء الطالبة."""

    focus_criteria = [
        item["title"]
        for item in support_needs[:3]
    ]

    if percentage < 60:
        recommendation_type = "remedial"
        title = "خطة علاجية"
        description = (
            "تحتاج الطالبة إلى دعم مركز ومتدرج "
            "لإتقان المهارات الأساسية."
        )
        actions = [
            "إعادة شرح المهارة باستخدام أمثلة مبسطة.",
            "تنفيذ نشاط موجه مع تغذية راجعة فورية.",
            "إعادة التقييم بعد تنفيذ الخطة العلاجية.",
        ]

    elif percentage < 80:
        recommendation_type = "development"
        title = "خطة تطويرية"
        description = (
            "أداء الطالبة في مستوى نامٍ، وتحتاج إلى "
            "ممارسات إضافية للوصول إلى الإتقان."
        )
        actions = [
            "تطبيق المهارة في موقف علمي جديد.",
            "استخدام أسئلة التفسير والاستدلال.",
            "متابعة التحسن في العمل القادم.",
        ]

    else:
        recommendation_type = "enrichment"
        title = "خطة إثرائية"
        description = (
            "أداء الطالبة مرتفع، وتوصى بأنشطة إثرائية "
            "تعزز التفكير العلمي والإبداع."
        )
        actions = [
            "تنفيذ بحث أو استقصاء علمي مصغر.",
            "تصميم منتج يطبق المفهوم العلمي.",
            "المشاركة في دعم التعلم التعاوني.",
        ]

    return {
        "type": recommendation_type,
        "title": title,
        "description": description,
        "actions": actions,
        "focus_criteria": focus_criteria,
    }