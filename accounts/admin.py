from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import StudentProfile, TeacherProfile, User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = (
        "username",
        "full_name",
        "email",
        "role",
        "phone",
        "is_active",
        "is_verified",
        "is_staff",
    )

    list_filter = (
        "role",
        "is_active",
        "is_verified",
        "is_staff",
        "is_superuser",
    )

    search_fields = (
        "username",
        "first_name",
        "last_name",
        "email",
        "phone",
    )

    ordering = (
        "first_name",
        "last_name",
        "username",
    )

    readonly_fields = (
        "last_login",
        "date_joined",
        "created_at",
        "updated_at",
    )

    fieldsets = BaseUserAdmin.fieldsets + (
        (
            "بيانات دفتر العلوم الذكي",
            {
                "fields": (
                    "role",
                    "phone",
                    "avatar",
                    "is_verified",
                    "created_at",
                    "updated_at",
                )
            },
        ),
    )

    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        (
            "بيانات الحساب",
            {
                "fields": (
                    "first_name",
                    "last_name",
                    "email",
                    "role",
                    "phone",
                    "is_verified",
                )
            },
        ),
    )

    @admin.display(
        description="الاسم الكامل",
        ordering="first_name",
    )
    def full_name(self, obj):
        return obj.get_full_name().strip() or obj.username


@admin.register(TeacherProfile)
class TeacherProfileAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "employee_number",
        "specialization",
        "qualification",
    )

    search_fields = (
        "user__username",
        "user__first_name",
        "user__last_name",
        "employee_number",
        "specialization",
    )

    list_select_related = (
        "user",
    )


@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "student_number",
        "guardian_name",
        "guardian_phone",
        "guardian_email",
    )

    search_fields = (
        "user__username",
        "user__first_name",
        "user__last_name",
        "student_number",
        "guardian_name",
        "guardian_phone",
        "guardian_email",
    )

    list_select_related = (
        "user",
    )