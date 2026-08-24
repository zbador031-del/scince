from django.contrib import admin

from .models import (
    AcademicYear,
    Classroom,
    Enrollment,
    GradeLevel,
    Lesson,
    School,
    Subject,
    TeachingAssignment,
    Term,
    Unit,
)


class EnrollmentInline(admin.TabularInline):
    model = Enrollment
    extra = 0
    fields = (
        "student",
        "status",
        "joined_at",
        "left_at",
    )
    readonly_fields = ("joined_at",)
    show_change_link = True


class TeachingAssignmentInline(admin.TabularInline):
    model = TeachingAssignment
    extra = 0
    fields = (
        "teacher",
        "subject",
        "is_active",
    )
    show_change_link = True


class LessonInline(admin.TabularInline):
    model = Lesson
    extra = 0
    fields = (
        "title",
        "order",
        "is_active",
    )
    show_change_link = True


@admin.register(School)
class SchoolAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "education_department",
        "principal_name",
        "phone",
        "is_active",
    )

    list_filter = (
        "is_active",
        "education_department",
    )

    search_fields = (
        "name",
        "education_department",
        "principal_name",
        "phone",
        "email",
    )


@admin.register(AcademicYear)
class AcademicYearAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "start_date",
        "end_date",
        "is_current",
    )

    list_filter = (
        "is_current",
    )

    search_fields = (
        "name",
    )

    ordering = (
        "-start_date",
    )


@admin.register(Term)
class TermAdmin(admin.ModelAdmin):
    list_display = (
        "academic_year",
        "number",
        "start_date",
        "end_date",
        "is_current",
    )

    list_filter = (
        "number",
        "is_current",
        "academic_year",
    )

    search_fields = (
        "academic_year__name",
    )

    list_select_related = (
        "academic_year",
    )


@admin.register(GradeLevel)
class GradeLevelAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "code",
        "order",
    )

    search_fields = (
        "name",
        "code",
    )

    ordering = (
        "order",
    )

    list_editable = (
        "order",
    )


@admin.register(Classroom)
class ClassroomAdmin(admin.ModelAdmin):
    list_display = (
        "grade_level",
        "name",
        "school",
        "academic_year",
        "homeroom_teacher",
        "student_count",
        "is_active",
    )

    list_filter = (
        "is_active",
        "school",
        "academic_year",
        "grade_level",
    )

    search_fields = (
        "name",
        "school__name",
        "grade_level__name",
        "homeroom_teacher__first_name",
        "homeroom_teacher__last_name",
    )

    list_select_related = (
        "school",
        "academic_year",
        "grade_level",
        "homeroom_teacher",
    )

    inlines = (
        EnrollmentInline,
        TeachingAssignmentInline,
    )

    @admin.display(description="عدد الطالبات")
    def student_count(self, obj):
        return obj.enrollments.filter(status="active").count()


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "code",
        "is_active",
    )

    list_filter = (
        "is_active",
    )

    search_fields = (
        "name",
        "code",
        "description",
    )


@admin.register(Unit)
class UnitAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "subject",
        "grade_level",
        "term",
        "order",
    )

    list_filter = (
        "subject",
        "grade_level",
        "term",
    )

    search_fields = (
        "title",
        "description",
        "subject__name",
        "grade_level__name",
    )

    list_select_related = (
        "subject",
        "grade_level",
        "term",
    )

    inlines = (
        LessonInline,
    )


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "unit",
        "order",
        "is_active",
    )

    list_filter = (
        "is_active",
        "unit__grade_level",
        "unit__term",
    )

    search_fields = (
        "title",
        "learning_objectives",
        "unit__title",
    )

    list_select_related = (
        "unit",
    )

    list_editable = (
        "order",
        "is_active",
    )


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = (
        "student",
        "classroom",
        "status",
        "joined_at",
        "left_at",
    )

    list_filter = (
        "status",
        "classroom__academic_year",
        "classroom__grade_level",
        "classroom",
    )

    search_fields = (
        "student__username",
        "student__first_name",
        "student__last_name",
        "classroom__name",
    )

    list_select_related = (
        "student",
        "classroom",
        "classroom__grade_level",
        "classroom__academic_year",
    )

    readonly_fields = (
        "joined_at",
    )


@admin.register(TeachingAssignment)
class TeachingAssignmentAdmin(admin.ModelAdmin):
    list_display = (
        "teacher",
        "subject",
        "classroom",
        "is_active",
    )

    list_filter = (
        "is_active",
        "subject",
        "classroom__grade_level",
        "classroom__academic_year",
    )

    search_fields = (
        "teacher__username",
        "teacher__first_name",
        "teacher__last_name",
        "subject__name",
        "classroom__name",
    )

    list_select_related = (
        "teacher",
        "subject",
        "classroom",
        "classroom__grade_level",
    )