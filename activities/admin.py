from django.contrib import admin

from .models import Activity, ActivityAssignment


class ActivityAssignmentInline(admin.TabularInline):
    model = ActivityAssignment
    extra = 0
    fields = (
        "classroom",
        "assigned_by",
        "assigned_at",
    )
    readonly_fields = (
        "assigned_at",
    )
    show_change_link = True


@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "activity_type",
        "subject",
        "term",
        "created_by",
        "max_score",
        "due_at",
        "is_published",
        "classroom_count",
    )

    list_filter = (
        "activity_type",
        "work_mode",
        "ai_policy",
        "is_published",
        "subject",
        "term",
    )

    search_fields = (
        "title",
        "description",
        "instructions",
        "subject__name",
        "unit__title",
        "lesson__title",
        "created_by__first_name",
        "created_by__last_name",
    )

    list_select_related = (
        "subject",
        "unit",
        "lesson",
        "term",
        "created_by",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    date_hierarchy = "created_at"

    inlines = (
        ActivityAssignmentInline,
    )

    @admin.display(description="عدد الشعب")
    def classroom_count(self, obj):
        return obj.classrooms.count()


@admin.register(ActivityAssignment)
class ActivityAssignmentAdmin(admin.ModelAdmin):
    list_display = (
        "activity",
        "classroom",
        "assigned_by",
        "assigned_at",
    )

    list_filter = (
        "classroom__academic_year",
        "classroom__grade_level",
        "classroom",
    )

    search_fields = (
        "activity__title",
        "classroom__name",
        "assigned_by__first_name",
        "assigned_by__last_name",
    )

    list_select_related = (
        "activity",
        "classroom",
        "classroom__grade_level",
        "assigned_by",
    )

    readonly_fields = (
        "assigned_at",
    )

    date_hierarchy = "assigned_at"