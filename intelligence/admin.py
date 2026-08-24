from django.contrib import admin

from .models import (
    AIAnalysis,
    AIUsageLog,
    PerformanceSnapshot,
    Recommendation,
)


@admin.register(AIAnalysis)
class AIAnalysisAdmin(admin.ModelAdmin):
    list_display = (
        "submission_version",
        "student_name",
        "status",
        "suggested_score",
        "confidence_score",
        "model_name",
        "created_at",
        "completed_at",
    )

    list_filter = (
        "status",
        "provider_name",
        "model_name",
        "created_at",
    )

    search_fields = (
        "submission_version__submission__title",
        "submission_version__submission__portfolio__student__first_name",
        "submission_version__submission__portfolio__student__last_name",
        "summary",
        "suggested_feedback",
        "model_name",
    )

    list_select_related = (
        "submission_version",
        "submission_version__submission",
        "submission_version__submission__portfolio",
        "submission_version__submission__portfolio__student",
        "requested_by",
    )

    readonly_fields = (
        "created_at",
        "completed_at",
    )

    date_hierarchy = "created_at"

    @admin.display(
        description="الطالبة",
        ordering=(
            "submission_version__submission__portfolio__student__first_name"
        ),
    )
    def student_name(self, obj):
        return obj.submission_version.submission.portfolio.student


@admin.register(AIUsageLog)
class AIUsageLogAdmin(admin.ModelAdmin):
    list_display = (
        "feature_name",
        "user",
        "provider_name",
        "model_name",
        "input_tokens",
        "output_tokens",
        "duration_ms",
        "was_successful",
        "created_at",
    )

    list_filter = (
        "was_successful",
        "provider_name",
        "model_name",
        "created_at",
    )

    search_fields = (
        "feature_name",
        "user__username",
        "user__first_name",
        "user__last_name",
        "provider_name",
        "model_name",
        "error_code",
    )

    list_select_related = (
        "user",
    )

    readonly_fields = (
        "user",
        "feature_name",
        "provider_name",
        "model_name",
        "input_tokens",
        "output_tokens",
        "duration_ms",
        "was_successful",
        "error_code",
        "created_at",
    )

    date_hierarchy = "created_at"

    def has_add_permission(self, request):
        return False


@admin.register(PerformanceSnapshot)
class PerformanceSnapshotAdmin(admin.ModelAdmin):
    list_display = (
        "student_name",
        "term",
        "total_activities",
        "submitted_activities",
        "approved_activities",
        "late_activities",
        "completion_rate",
        "average_score",
        "risk_level",
        "generated_at",
    )

    list_filter = (
        "risk_level",
        "term",
        "portfolio__classroom",
        "generated_at",
    )

    search_fields = (
        "portfolio__student__first_name",
        "portfolio__student__last_name",
        "portfolio__student__username",
    )

    list_select_related = (
        "portfolio",
        "portfolio__student",
        "portfolio__classroom",
        "term",
    )

    readonly_fields = (
        "generated_at",
    )

    date_hierarchy = "generated_at"

    @admin.display(
        description="الطالبة",
        ordering="portfolio__student__first_name",
    )
    def student_name(self, obj):
        return obj.portfolio.student


@admin.register(Recommendation)
class RecommendationAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "student_name",
        "recommendation_type",
        "priority",
        "status",
        "created_by_ai",
        "reviewed_by",
        "created_at",
    )

    list_filter = (
        "recommendation_type",
        "status",
        "created_by_ai",
        "priority",
        "portfolio__classroom",
    )

    search_fields = (
        "title",
        "description",
        "portfolio__student__first_name",
        "portfolio__student__last_name",
        "lesson__title",
    )

    list_select_related = (
        "portfolio",
        "portfolio__student",
        "portfolio__classroom",
        "lesson",
        "reviewed_by",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    date_hierarchy = "created_at"

    @admin.display(
        description="الطالبة",
        ordering="portfolio__student__first_name",
    )
    def student_name(self, obj):
        return obj.portfolio.student