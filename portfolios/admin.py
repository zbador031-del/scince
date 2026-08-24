from django.contrib import admin

from .models import (
    Attachment,
    Portfolio,
    PortfolioSection,
    Submission,
    SubmissionComment,
    SubmissionVersion,
)


class PortfolioSectionInline(admin.TabularInline):
    model = PortfolioSection
    extra = 0
    fields = (
        "title",
        "unit",
        "order",
    )
    show_change_link = True


class SubmissionVersionInline(admin.TabularInline):
    model = SubmissionVersion
    extra = 0
    fields = (
        "version_number",
        "ai_used",
        "is_current",
        "submitted_at",
    )
    readonly_fields = (
        "submitted_at",
    )
    show_change_link = True


class AttachmentInline(admin.TabularInline):
    model = Attachment
    extra = 0
    fields = (
        "file",
        "media_type",
        "caption",
        "size_bytes",
        "uploaded_at",
    )
    readonly_fields = (
        "size_bytes",
        "uploaded_at",
    )
    show_change_link = True


@admin.register(Portfolio)
class PortfolioAdmin(admin.ModelAdmin):
    list_display = (
        "student",
        "title",
        "classroom",
        "subject",
        "academic_year",
        "submission_count",
        "is_active",
        "updated_at",
    )

    list_filter = (
        "is_active",
        "academic_year",
        "subject",
        "classroom__grade_level",
        "classroom",
    )

    search_fields = (
        "title",
        "student__username",
        "student__first_name",
        "student__last_name",
        "classroom__name",
        "subject__name",
    )

    list_select_related = (
        "student",
        "classroom",
        "classroom__grade_level",
        "subject",
        "academic_year",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    inlines = (
        PortfolioSectionInline,
    )

    @admin.display(description="عدد الأعمال")
    def submission_count(self, obj):
        return obj.submissions.count()


@admin.register(PortfolioSection)
class PortfolioSectionAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "portfolio",
        "unit",
        "order",
    )

    list_filter = (
        "unit__grade_level",
        "unit__term",
    )

    search_fields = (
        "title",
        "portfolio__student__first_name",
        "portfolio__student__last_name",
        "unit__title",
    )

    list_select_related = (
        "portfolio",
        "portfolio__student",
        "unit",
    )

    list_editable = (
        "order",
    )


@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "student_name",
        "activity",
        "status",
        "is_featured",
        "submitted_at",
        "updated_at",
    )

    list_filter = (
        "status",
        "is_featured",
        "activity__activity_type",
        "portfolio__classroom",
    )

    search_fields = (
        "title",
        "description",
        "portfolio__student__username",
        "portfolio__student__first_name",
        "portfolio__student__last_name",
        "activity__title",
    )

    list_select_related = (
        "portfolio",
        "portfolio__student",
        "activity",
        "section",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    date_hierarchy = "created_at"

    filter_horizontal = (
        "collaborators",
    )

    inlines = (
        SubmissionVersionInline,
    )

    @admin.display(
        description="الطالبة",
        ordering="portfolio__student__first_name",
    )
    def student_name(self, obj):
        return obj.portfolio.student


@admin.register(SubmissionVersion)
class SubmissionVersionAdmin(admin.ModelAdmin):
    list_display = (
        "submission",
        "version_number",
        "ai_used",
        "is_current",
        "attachment_count",
        "submitted_at",
    )

    list_filter = (
        "ai_used",
        "is_current",
        "submission__status",
    )

    search_fields = (
        "submission__title",
        "submission__portfolio__student__first_name",
        "submission__portfolio__student__last_name",
        "ai_tools",
        "reflection",
    )

    list_select_related = (
        "submission",
        "submission__portfolio",
        "submission__portfolio__student",
    )

    readonly_fields = (
        "submitted_at",
    )

    inlines = (
        AttachmentInline,
    )

    @admin.display(description="عدد المرفقات")
    def attachment_count(self, obj):
        return obj.attachments.count()


@admin.register(Attachment)
class AttachmentAdmin(admin.ModelAdmin):
    list_display = (
        "original_filename",
        "version",
        "media_type",
        "size_bytes",
        "uploaded_at",
    )

    list_filter = (
        "media_type",
        "uploaded_at",
    )

    search_fields = (
        "original_filename",
        "caption",
        "version__submission__title",
        "version__submission__portfolio__student__first_name",
        "version__submission__portfolio__student__last_name",
    )

    list_select_related = (
        "version",
        "version__submission",
    )

    readonly_fields = (
        "original_filename",
        "size_bytes",
        "uploaded_at",
    )

    date_hierarchy = "uploaded_at"


@admin.register(SubmissionComment)
class SubmissionCommentAdmin(admin.ModelAdmin):
    list_display = (
        "submission",
        "author",
        "is_private",
        "created_at",
    )

    list_filter = (
        "is_private",
        "created_at",
    )

    search_fields = (
        "submission__title",
        "author__first_name",
        "author__last_name",
        "body",
    )

    list_select_related = (
        "submission",
        "author",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    date_hierarchy = "created_at"