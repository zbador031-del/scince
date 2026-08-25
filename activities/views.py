from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import (
    require_GET,
    require_http_methods,
)

from academics.models import Enrollment, Term
from portfolios.models import Submission

from .forms import ActivityForm
from .models import Activity, ActivityAssignment


def _ensure_teacher(user):
    """السماح للمعلمة أو مديرة النظام فقط."""

    if user.is_superuser:
        return

    if getattr(user, "role", None) != "teacher":
        raise PermissionDenied(
            "هذه الصفحة مخصصة للمعلمات فقط."
        )


def _ensure_student(user):
    """السماح للطالبات فقط."""

    if getattr(user, "role", None) != "student":
        raise PermissionDenied(
            "هذه الصفحة مخصصة للطالبات فقط."
        )


def _teacher_activities(user):
    """الأنشطة التي تملك المعلمة صلاحية إدارتها."""

    activities = Activity.objects.select_related(
        "subject",
        "unit",
        "lesson",
        "term",
        "created_by",
    ).prefetch_related(
        "classrooms"
    )

    if user.is_superuser:
        return activities

    return activities.filter(
        created_by=user
    )


def _get_student_enrollment(user):
    """التسجيل الدراسي النشط للطالبة."""

    return (
        Enrollment.objects.filter(
            student=user,
            status=Enrollment.Status.ACTIVE,
            classroom__is_active=True,
        )
        .select_related(
            "classroom",
            "classroom__grade_level",
        )
        .first()
    )


def _student_activities(user):
    """الأنشطة المنشورة لفصل الطالبة."""

    enrollment = _get_student_enrollment(user)

    if enrollment is None:
        return Activity.objects.none(), None

    activities = (
        Activity.objects.filter(
            classroom_assignments__classroom=(
                enrollment.classroom
            ),
            is_published=True,
        )
        .select_related(
            "subject",
            "unit",
            "lesson",
            "term",
            "created_by",
        )
        .distinct()
        .order_by(
            "due_at",
            "-created_at",
        )
    )

    return activities, enrollment


def _set_activity_time_status(activity):
    """حساب حالة إتاحة النشاط وفق الوقت."""

    now = timezone.now()

    has_opened = (
        activity.opens_at is None
        or activity.opens_at <= now
    )

    is_before_deadline = (
        activity.due_at is None
        or activity.due_at >= now
    )

    activity.has_opened = has_opened
    activity.is_late = (
        activity.due_at is not None
        and activity.due_at < now
    )

    activity.can_submit = (
        has_opened
        and (
            is_before_deadline
            or activity.allow_late_submission
        )
    )

    return activity


@login_required
@require_GET
def teacher_activity_list(request):
    """قائمة الأنشطة الخاصة بالمعلمة."""

    _ensure_teacher(request.user)

    activities = _teacher_activities(
        request.user
    ).order_by(
        "-created_at"
    )

    context = {
        "activities": activities,
    }

    return render(
        request,
        "activities/teacher_activity_list.html",
        context,
    )


@login_required
@require_http_methods(["GET", "POST"])
def teacher_activity_create(request):
    """إنشاء نشاط وإسناده إلى عدة فصول."""

    _ensure_teacher(request.user)

    current_term = Term.objects.filter(
        is_current=True
    ).first()

    if request.method == "POST":
        form = ActivityForm(
            request.POST,
            request.FILES,
            teacher=request.user,
        )

        if form.is_valid():
            classrooms = form.cleaned_data[
                "classrooms"
            ]

            with transaction.atomic():
                activity = form.save(commit=False)
                activity.created_by = request.user

                if not activity.allowed_extensions:
                    activity.allowed_extensions = [
                        "pdf",
                        "doc",
                        "docx",
                        "ppt",
                        "pptx",
                        "jpg",
                        "jpeg",
                        "png",
                        "webp",
                        "mp4",
                        "mov",
                        "webm",
                        "mp3",
                        "wav",
                        "m4a",
                    ]

                activity.save()

                ActivityAssignment.objects.bulk_create(
                    [
                        ActivityAssignment(
                            activity=activity,
                            classroom=classroom,
                            assigned_by=request.user,
                        )
                        for classroom in classrooms
                    ]
                )

            messages.success(
                request,
                "تم إنشاء النشاط وإسناده للفصول بنجاح.",
            )

            return redirect(
                "activities:teacher_activity_list"
            )
    else:
        initial = {}

        if current_term is not None:
            initial["term"] = current_term

        form = ActivityForm(
            teacher=request.user,
            initial=initial,
        )

    context = {
        "form": form,
        "page_title": "إنشاء نشاط جديد",
        "submit_label": "حفظ ونشر النشاط",
    }

    return render(
        request,
        "activities/activity_form.html",
        context,
    )


@login_required
@require_http_methods(["GET", "POST"])
def teacher_activity_update(request, activity_id):
    """تعديل نشاط موجود."""

    _ensure_teacher(request.user)

    activity = get_object_or_404(
        _teacher_activities(request.user),
        pk=activity_id,
    )

    if request.method == "POST":
        form = ActivityForm(
            request.POST,
            request.FILES,
            instance=activity,
            teacher=request.user,
        )

        if form.is_valid():
            selected_classrooms = set(
                form.cleaned_data[
                    "classrooms"
                ].values_list(
                    "id",
                    flat=True,
                )
            )

            with transaction.atomic():
                activity = form.save()

                current_assignments = (
                    ActivityAssignment.objects.filter(
                        activity=activity
                    )
                )

                current_classroom_ids = set(
                    current_assignments.values_list(
                        "classroom_id",
                        flat=True,
                    )
                )

                removed_ids = (
                    current_classroom_ids
                    - selected_classrooms
                )

                added_ids = (
                    selected_classrooms
                    - current_classroom_ids
                )

                if removed_ids:
                    current_assignments.filter(
                        classroom_id__in=removed_ids
                    ).delete()

                ActivityAssignment.objects.bulk_create(
                    [
                        ActivityAssignment(
                            activity=activity,
                            classroom_id=classroom_id,
                            assigned_by=request.user,
                        )
                        for classroom_id in added_ids
                    ]
                )

            messages.success(
                request,
                "تم تحديث النشاط بنجاح.",
            )

            return redirect(
                "activities:teacher_activity_list"
            )
    else:
        form = ActivityForm(
            instance=activity,
            teacher=request.user,
        )

    context = {
        "form": form,
        "activity": activity,
        "page_title": "تعديل النشاط",
        "submit_label": "حفظ التعديلات",
    }

    return render(
        request,
        "activities/activity_form.html",
        context,
    )


@login_required
@require_GET
def student_activity_list(request):
    """قائمة الأنشطة المطلوبة من الطالبة."""

    _ensure_student(request.user)

    activities, enrollment = _student_activities(
        request.user
    )

    submissions = Submission.objects.filter(
        portfolio__student=request.user,
        activity__in=activities,
    ).select_related(
        "activity"
    )

    submission_map = {
        submission.activity_id: submission
        for submission in submissions
    }

    activity_list = []

    for activity in activities:
        _set_activity_time_status(activity)

        activity.student_submission = (
            submission_map.get(activity.id)
        )

        activity_list.append(activity)

    context = {
        "activities": activity_list,
        "enrollment": enrollment,
    }

    return render(
        request,
        "activities/student_activity_list.html",
        context,
    )


@login_required
@require_GET
def student_activity_detail(request, activity_id):
    """عرض تفاصيل نشاط مطلوب للطالبة."""

    _ensure_student(request.user)

    activities, enrollment = _student_activities(
        request.user
    )

    activity = get_object_or_404(
        activities,
        pk=activity_id,
    )

    _set_activity_time_status(activity)

    submission = Submission.objects.filter(
        portfolio__student=request.user,
        activity=activity,
    ).first()

    context = {
        "activity": activity,
        "enrollment": enrollment,
        "submission": submission,
    }

    return render(
        request,
        "activities/student_activity_detail.html",
        context,
    )