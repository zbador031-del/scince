from django.contrib import admin
from django.utils import timezone

from .models import (
    AIAnalysis,
    AIUsageLog,
    MonthlyHonor,
    PerformanceSnapshot,
    Recommendation,
)


@admin.register(AIAnalysis)
class AIAnalysisAdmin(admin.ModelAdmin):
    """إدارة التحليلات الذكية."""

    list_per_page = 25


@admin.register(AIUsageLog)
class AIUsageLogAdmin(admin.ModelAdmin):
    """إدارة سجلات استخدام الذكاء الاصطناعي."""

    list_per_page = 25


@admin.register(PerformanceSnapshot)
class PerformanceSnapshotAdmin(admin.ModelAdmin):
    """إدارة لقطات أداء الطالبات."""

    list_per_page = 25


@admin.register(Recommendation)
class RecommendationAdmin(admin.ModelAdmin):
    """إدارة التوصيات."""

    list_per_page = 25


@admin.register(MonthlyHonor)
class MonthlyHonorAdmin(admin.ModelAdmin):
    """إدارة عالمة الشهر والشريط المتحرك."""

    list_display = (
        "hijri_month_label",
        "student",
        "classroom",
        "average_score",
        "completion_rate",
        "improvement_rate",
        "is_approved",
        "is_active_in_ticker",
        "approved_by",
    )

    list_filter = (
        "is_approved",
        "is_active_in_ticker",
        "publish_student_name",
        "classroom__grade_level",
        "classroom",
        "month_start",
    )

    search_fields = (
        "student__first_name",
        "student__last_name",
        "student__username",
        "hijri_month_label",
        "selection_reason",
        "ticker_message",
    )

    list_select_related = (
        "student",
        "classroom",
        "classroom__grade_level",
        "featured_submission",
        "approved_by",
    )

    raw_id_fields = (
        "student",
        "featured_submission",
    )

    readonly_fields = (
        "approved_by",
        "approved_at",
        "created_at",
        "updated_at",
    )

    fieldsets = (
        (
            "بيانات الشهر والطالبة",
            {
                "fields": (
                    "student",
                    "classroom",
                    "month_start",
                    "month_end",
                    "hijri_month_label",
                )
            },
        ),
        (
            "مؤشرات الأداء",
            {
                "fields": (
                    "average_score",
                    "completion_rate",
                    "improvement_rate",
                    "submitted_activities",
                    "approved_activities",
                    "featured_activities",
                    "featured_submission",
                )
            },
        ),
        (
            "التكريم والشريط المتحرك",
            {
                "fields": (
                    "selection_reason",
                    "ticker_message",
                    "publish_student_name",
                    "is_approved",
                    "is_active_in_ticker",
                )
            },
        ),
        (
            "بيانات الاعتماد",
            {
                "fields": (
                    "approved_by",
                    "approved_at",
                    "created_at",
                    "updated_at",
                )
            },
        ),
    )

    date_hierarchy = "month_start"
    list_per_page = 25

    def save_model(self, request, obj, form, change):
        """حفظ بيانات اعتماد عالمة الشهر تلقائيًا."""

        if obj.is_approved:
            if obj.approved_at is None:
                obj.approved_at = timezone.now()

            obj.approved_by = request.user

        else:
            obj.approved_at = None
            obj.approved_by = None
            obj.is_active_in_ticker = False

        super().save_model(request, obj, form, change)