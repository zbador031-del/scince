from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import (
    require_http_methods,
    require_POST,
)

from academics.models import TeachingAssignment
from portfolios.models import Submission, SubmissionVersion

from .forms import (
    BulkEvaluationForm,
    EvaluationDecision,
    EvaluationForm,
)
from .models import Evaluation


def _ensure_teacher(user):
    """السماح للمعلمة أو مديرة النظام فقط."""

    if user.is_superuser:
        return

    if getattr(user, "role", None) != "teacher":
        raise PermissionDenied(
            "هذه الصفحة مخصصة للمعلمات فقط."
        )


def _allowed_submissions(user):
    """الأعمال التي يحق للمعلمة تقييمها."""

    submissions = Submission.objects.select_related(
        "portfolio",
        "portfolio__student",
        "portfolio__classroom",
        "portfolio__subject",
    ).prefetch_related(
        "versions__attachments"
    )

    if user.is_superuser:
        return submissions

    classroom_ids = TeachingAssignment.objects.filter(
        teacher=user,
        is_active=True,
    ).values_list(
        "classroom_id",
        flat=True,
    )

    return submissions.filter(
        portfolio__classroom_id__in=classroom_ids
    )


def _decision_from_submission(submission):
    """تحديد القرار الحالي للعمل."""

    if submission.status == Submission.Status.APPROVED:
        return EvaluationDecision.APPROVED

    if submission.status == Submission.Status.FEATURED:
        return EvaluationDecision.FEATURED

    if submission.status == Submission.Status.REVISION_REQUIRED:
        return EvaluationDecision.REVISION_REQUIRED

    return EvaluationDecision.DRAFT


def _apply_evaluation(
    *,
    submission,
    version,
    evaluator,
    rubric,
    total_score,
    general_feedback,
    decision,
):
    """حفظ التقييم وتحديث حالة العمل."""

    if decision == EvaluationDecision.DRAFT:
        evaluation_status = Evaluation.Status.DRAFT
        published_at = None
        submission_status = Submission.Status.UNDER_REVIEW
        is_featured = False

    elif decision == EvaluationDecision.REVISION_REQUIRED:
        evaluation_status = Evaluation.Status.REVISION_REQUIRED
        published_at = timezone.now()
        submission_status = Submission.Status.REVISION_REQUIRED
        is_featured = False

    elif decision == EvaluationDecision.FEATURED:
        evaluation_status = Evaluation.Status.PUBLISHED
        published_at = timezone.now()
        submission_status = Submission.Status.FEATURED
        is_featured = True

    else:
        evaluation_status = Evaluation.Status.PUBLISHED
        published_at = timezone.now()
        submission_status = Submission.Status.APPROVED
        is_featured = False

    evaluation, created = Evaluation.objects.update_or_create(
        submission_version=version,
        defaults={
            "evaluator": evaluator,
            "rubric": rubric,
            "total_score": total_score,
            "general_feedback": general_feedback.strip(),
            "status": evaluation_status,
            "published_at": published_at,
        },
    )

    submission.status = submission_status
    submission.is_featured = is_featured
    submission.save(
        update_fields=[
            "status",
            "is_featured",
            "updated_at",
        ]
    )

    return evaluation


@login_required
@require_http_methods(["GET", "POST"])
def evaluate_submission(request, submission_id):
    """تقييم عمل طالبة واحدة."""

    _ensure_teacher(request.user)

    submission = get_object_or_404(
        _allowed_submissions(request.user),
        pk=submission_id,
    )

    version = get_object_or_404(
        SubmissionVersion.objects.prefetch_related(
            "attachments"
        ),
        submission=submission,
        is_current=True,
    )

    try:
        existing_evaluation = version.evaluation
    except Evaluation.DoesNotExist:
        existing_evaluation = None

    initial_data = {
        "decision": _decision_from_submission(submission),
    }

    if existing_evaluation is not None:
        initial_data.update(
            {
                "rubric": existing_evaluation.rubric,
                "total_score": existing_evaluation.total_score,
                "general_feedback": (
                    existing_evaluation.general_feedback
                ),
            }
        )

    if request.method == "POST":
        form = EvaluationForm(
            request.POST,
            teacher=request.user,
            subject=submission.portfolio.subject,
        )

        if form.is_valid():
            with transaction.atomic():
                _apply_evaluation(
                    submission=submission,
                    version=version,
                    evaluator=request.user,
                    rubric=form.cleaned_data["rubric"],
                    total_score=form.cleaned_data["total_score"],
                    general_feedback=form.cleaned_data[
                        "general_feedback"
                    ],
                    decision=form.cleaned_data["decision"],
                )

            messages.success(
                request,
                "تم حفظ تقييم الطالبة بنجاح.",
            )

            return redirect(
                "portfolios:teacher_submission_detail",
                submission_id=submission.id,
            )
    else:
        form = EvaluationForm(
            initial=initial_data,
            teacher=request.user,
            subject=submission.portfolio.subject,
        )

    context = {
        "submission": submission,
        "version": version,
        "form": form,
        "existing_evaluation": existing_evaluation,
    }

    return render(
        request,
        "assessment/evaluate_submission.html",
        context,
    )


@login_required
@require_POST
def bulk_evaluate_submissions(request):
    """تطبيق تقييم موحد على عدة أعمال."""

    _ensure_teacher(request.user)

    selected_ids = request.POST.getlist("submission_ids")

    if not selected_ids:
        messages.error(
            request,
            "حددي عملًا واحدًا على الأقل للتقييم.",
        )
        return redirect(
            "portfolios:teacher_submissions"
        )

    submissions = _allowed_submissions(
        request.user
    ).filter(
        id__in=selected_ids
    )

    form = BulkEvaluationForm(
        request.POST,
        teacher=request.user,
    )

    if not form.is_valid():
        error_message = "تحققي من بيانات التقييم الجماعي."

        for field_errors in form.errors.values():
            if field_errors:
                error_message = field_errors[0]
                break

        messages.error(request, error_message)

        return redirect(
            "portfolios:teacher_submissions"
        )

    evaluated_count = 0

    with transaction.atomic():
        for submission in submissions:
            version = submission.versions.filter(
                is_current=True
            ).first()

            if version is None:
                continue

            _apply_evaluation(
                submission=submission,
                version=version,
                evaluator=request.user,
                rubric=form.cleaned_data["rubric"],
                total_score=form.cleaned_data["total_score"],
                general_feedback=form.cleaned_data[
                    "general_feedback"
                ],
                decision=form.cleaned_data["decision"],
            )

            evaluated_count += 1

    messages.success(
        request,
        f"تم تقييم واعتماد {evaluated_count} عمل بنجاح.",
    )

    return redirect(
        "portfolios:teacher_submissions"
    )