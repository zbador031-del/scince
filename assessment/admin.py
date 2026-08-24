from django.contrib import admin

from .models import (
    ActivityRubric,
    Badge,
    CriterionScore,
    Evaluation,
    Rubric,
    RubricCriterion,
    StudentBadge,
)


class RubricCriterionInline(admin.TabularInline):
    model = RubricCriterion
    extra = 0
    fields = (
        "title",
        "description",
        "max_points",
        "order",
    )
    show_change_link = True


class CriterionScoreInline(admin.TabularInline):
    model = CriterionScore
    extra = 0
    fields = (
        "criterion",
        "score",
        "feedback",
    )
    show_change_link = True


@admin.register(Rubric)
class RubricAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "subject",
        "created_by",
        "criteria_count",
        "maximum_points",
        "is_active",
        "created_at",
    )

    list_filter = (
        "is_active",
        "subject",
        "created_at",
    )

    search_fields = (
        "title",
        "description",
        "subject__name",
        "created_by__first_name",
        "created_by__last_name",
    )

    list_select_related = (
        "subject",
        "created_by",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    inlines = (
        RubricCriterionInline,
    )

    @admin.display(description="عدد المعايير")
    def criteria_count(self, obj):
        return obj.criteria.count()

    @admin.display(description="مجموع الدرجات")
    def maximum_points(self, obj):
        return obj.maximum_score


@admin.register(RubricCriterion)
class RubricCriterionAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "rubric",
        "max_points",
        "order",
    )

    list_filter = (
        "rubric",
    )

    search_fields = (
        "title",
        "description",
        "rubric__title",
    )

    list_select_related = (
        "rubric",
    )

    list_editable = (
        "max_points",
        "order",
    )


@admin.register(ActivityRubric)
class ActivityRubricAdmin(admin.ModelAdmin):
    list_display = (
        "activity",
        "rubric",
        "assigned_by",
        "assigned_at",
    )

    list_filter = (
        "rubric",
        "activity__activity_type",
    )

    search_fields = (
        "activity__title",
        "rubric__title",
        "assigned_by__first_name",
        "assigned_by__last_name",
    )

    list_select_related = (
        "activity",
        "rubric",
        "assigned_by",
    )

    readonly_fields = (
        "assigned_at",
    )


@admin.register(Evaluation)
class EvaluationAdmin(admin.ModelAdmin):
    list_display = (
        "submission_version",
        "student_name",
        "evaluator",
        "rubric",
        "total_score",
        "status",
        "evaluated_at",
    )

    list_filter = (
        "status",
        "rubric",
        "evaluated_at",
    )

    search_fields = (
        "submission_version__submission__title",
        "submission_version__submission__portfolio__student__first_name",
        "submission_version__submission__portfolio__student__last_name",
        "evaluator__first_name",
        "evaluator__last_name",
        "general_feedback",
    )

    list_select_related = (
        "submission_version",
        "submission_version__submission",
        "submission_version__submission__portfolio",
        "submission_version__submission__portfolio__student",
        "evaluator",
        "rubric",
    )

    readonly_fields = (
        "evaluated_at",
    )

    date_hierarchy = "evaluated_at"

    inlines = (
        CriterionScoreInline,
    )

    @admin.display(
        description="الطالبة",
        ordering=(
            "submission_version__submission__portfolio__student__first_name"
        ),
    )
    def student_name(self, obj):
        return obj.submission_version.submission.portfolio.student


@admin.register(CriterionScore)
class CriterionScoreAdmin(admin.ModelAdmin):
    list_display = (
        "evaluation",
        "criterion",
        "score",
    )

    list_filter = (
        "criterion__rubric",
    )

    search_fields = (
        "evaluation__submission_version__submission__title",
        "criterion__title",
        "feedback",
    )

    list_select_related = (
        "evaluation",
        "criterion",
    )


@admin.register(Badge)
class BadgeAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "color",
        "is_active",
    )

    list_filter = (
        "is_active",
    )

    search_fields = (
        "name",
        "description",
    )


@admin.register(StudentBadge)
class StudentBadgeAdmin(admin.ModelAdmin):
    list_display = (
        "badge",
        "student_name",
        "submission",
        "awarded_by",
        "awarded_at",
    )

    list_filter = (
        "badge",
        "awarded_at",
        "portfolio__classroom",
    )

    search_fields = (
        "badge__name",
        "portfolio__student__first_name",
        "portfolio__student__last_name",
        "submission__title",
        "reason",
    )

    list_select_related = (
        "portfolio",
        "portfolio__student",
        "badge",
        "submission",
        "awarded_by",
    )

    readonly_fields = (
        "awarded_at",
    )

    date_hierarchy = "awarded_at"

    @admin.display(
        description="الطالبة",
        ordering="portfolio__student__first_name",
    )
    def student_name(self, obj):
        return obj.portfolio.student