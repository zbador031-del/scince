import mimetypes
import logging
from pathlib import Path

from cloudinary.exceptions import Error as CloudinaryError
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_GET, require_http_methods

from academics.models import Classroom, TeachingAssignment
from assessment.forms import BulkEvaluationForm

from .forms import StudentSubmissionForm
from .models import (
    Attachment,
    Portfolio,
    Submission,
    SubmissionVersion,
)


logger = logging.getLogger(__name__)


def _ensure_student(user):
    """السماح للطالبات فقط باستخدام صفحات الدفتر."""

    if getattr(user, "role", None) != "student":
        raise PermissionDenied(
            "هذه الصفحة مخصصة للطالبات فقط."
        )


def _ensure_teacher(user):
    """السماح للمعلمة أو مديرة النظام فقط."""

    if user.is_superuser:
        return

    if getattr(user, "role", None) != "teacher":
        raise PermissionDenied(
            "هذه الصفحة مخصصة للمعلمات فقط."
        )


def _get_student_portfolio(user):
    """إحضار الدفتر النشط الخاص بالطالبة."""

    return get_object_or_404(
        Portfolio.objects.select_related(
            "classroom",
            "subject",
            "academic_year",
        ),
        student=user,
        is_active=True,
    )


def _teacher_classroom_ids(user):
    """معرفة الشعب المسموح للمعلمة بمتابعتها."""

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


def _teacher_submission_queryset(user):
    """الأعمال التي يحق للمعلمة الاطلاع عليها."""

    classroom_ids = _teacher_classroom_ids(user)

    return (
        Submission.objects.filter(
            portfolio__classroom_id__in=classroom_ids,
            portfolio__is_active=True,
        )
        .select_related(
            "portfolio",
            "portfolio__student",
            "portfolio__classroom",
            "portfolio__subject",
            "section",
            "activity",
        )
        .prefetch_related(
            "versions__attachments",
            "comments__author",
        )
        .order_by("-created_at")
    )


@login_required
@require_GET
def student_portfolio(request):
    """عرض دفتر الطالبة وجميع أعمالها."""

    _ensure_student(request.user)
    portfolio = _get_student_portfolio(request.user)

    submissions = (
        Submission.objects.filter(
            portfolio=portfolio
        )
        .select_related(
            "section",
            "activity",
        )
        .prefetch_related(
            "versions__attachments",
            "comments__author",
        )
        .order_by("-created_at")
    )

    context = {
        "portfolio": portfolio,
        "submissions": submissions,
    }

    return render(
        request,
        "portfolios/student_portfolio.html",
        context,
    )


@login_required
@require_http_methods(["GET", "POST"])
def upload_submission(request):
    """رفع عمل جديد مع ملف مرفق إلى دفتر الطالبة."""

    _ensure_student(request.user)
    portfolio = _get_student_portfolio(request.user)

    if request.method == "POST":
        form = StudentSubmissionForm(
            request.POST,
            request.FILES,
            portfolio=portfolio,
        )

        if form.is_valid():
            uploaded_file = form.cleaned_data["file"]

            detected_mime_type = (
                getattr(
                    uploaded_file,
                    "content_type",
                    "",
                )
                or mimetypes.guess_type(
                    uploaded_file.name
                )[0]
                or "application/octet-stream"
            )

            try:
                with transaction.atomic():
                    submission = Submission.objects.create(
                        portfolio=portfolio,
                        section=form.cleaned_data.get(
                            "section"
                        ),
                        title=form.cleaned_data[
                            "title"
                        ].strip(),
                        description=form.cleaned_data[
                            "description"
                        ].strip(),
                        status=Submission.Status.SUBMITTED,
                        submitted_at=timezone.now(),
                    )

                    version = SubmissionVersion.objects.create(
                        submission=submission,
                        version_number=1,
                        reflection=form.cleaned_data[
                            "reflection"
                        ].strip(),
                        ai_used=form.cleaned_data[
                            "ai_used"
                        ],
                        ai_tools=form.cleaned_data[
                            "ai_tools"
                        ].strip(),
                        ai_usage_description=form.cleaned_data[
                            "ai_usage_description"
                        ].strip(),
                        is_current=True,
                    )

                    Attachment.objects.create(
                        version=version,
                        file=uploaded_file,
                        media_type=form.cleaned_data[
                            "media_type"
                        ],
                        caption=form.cleaned_data[
                            "caption"
                        ].strip(),
                        original_filename=Path(
                            uploaded_file.name
                        ).name,
                        mime_type=detected_mime_type[:100],
                        size_bytes=uploaded_file.size,
                    )
            except (CloudinaryError, OSError):
                logger.exception(
                    "تعذر رفع مرفق دفتر الطالبة إلى التخزين السحابي."
                )
                form.add_error(
                    "file",
                    (
                        "تعذر رفع الملف حاليًا. تأكدي أن حجمه أقل من "
                        "100 ميجابايت، ثم أعيدي المحاولة."
                    ),
                )
            else:
                messages.success(
                    request,
                    "تم رفع العمل وإرساله إلى المعلمة بنجاح.",
                )

                return redirect(
                    "portfolios:student_portfolio"
                )
    else:
        form = StudentSubmissionForm(
            portfolio=portfolio
        )

    context = {
        "portfolio": portfolio,
        "form": form,
    }

    return render(
        request,
        "portfolios/upload_submission.html",
        context,
    )


@login_required
@require_GET
def teacher_submissions(request):
    """عرض أعمال طالبات الشعب المسندة للمعلمة."""

    _ensure_teacher(request.user)

    submissions = _teacher_submission_queryset(
        request.user
    )

    classroom_id = request.GET.get(
        "classroom",
        "",
    ).strip()

    status = request.GET.get(
        "status",
        "",
    ).strip()

    if classroom_id.isdigit():
        submissions = submissions.filter(
            portfolio__classroom_id=int(
                classroom_id
            )
        )

    valid_statuses = {
        value
        for value, label in Submission.Status.choices
    }

    if status in valid_statuses:
        submissions = submissions.filter(
            status=status
        )

    classrooms = (
        Classroom.objects.filter(
            id__in=_teacher_classroom_ids(
                request.user
            )
        )
        .select_related("grade_level")
        .order_by(
            "grade_level__order",
            "name",
        )
    )

    context = {
        "submissions": submissions,
        "classrooms": classrooms,
        "selected_classroom": classroom_id,
        "selected_status": status,
        "status_choices": Submission.Status.choices,
        "bulk_form": BulkEvaluationForm(
            teacher=request.user
        ),
    }

    return render(
        request,
        "portfolios/teacher_submissions.html",
        context,
    )


@login_required
@require_GET
def teacher_submission_detail(
    request,
    submission_id,
):
    """عرض تفاصيل عمل طالبة للمعلمة."""

    _ensure_teacher(request.user)

    submission = get_object_or_404(
        _teacher_submission_queryset(
            request.user
        ),
        pk=submission_id,
    )

    current_version = (
        submission.versions.filter(
            is_current=True
        )
        .prefetch_related("attachments")
        .first()
    )

    if submission.status in {
        Submission.Status.SUBMITTED,
        Submission.Status.RESUBMITTED,
    }:
        submission.status = (
            Submission.Status.UNDER_REVIEW
        )

        submission.save(
            update_fields=[
                "status",
                "updated_at",
            ]
        )

    context = {
        "submission": submission,
        "current_version": current_version,
    }

    return render(
        request,
        "portfolios/teacher_submission_detail.html",
        context,
    )
