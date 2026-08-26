from django.contrib import admin
from django.contrib.auth.admin import (
    UserAdmin as BaseUserAdmin,
)
from django.contrib.auth.forms import (
    UserChangeForm,
    UserCreationForm,
)
from django.core.exceptions import ValidationError

from .models import (
    StudentProfile,
    TeacherProfile,
    User,
)


class OptionalContactFieldsMixin:
    """السماح بترك البريد والجوال فارغين دون تعارض."""

    def clean_email(self):
        email = self.cleaned_data.get("email")

        if not email:
            return None

        return email.strip().lower()

    def clean_phone(self):
        phone = self.cleaned_data.get("phone")

        if not phone:
            return None

        return phone.strip()

    def validate_unique(self):
        """استثناء البريد والجوال الفارغين من فحص التكرار."""

        exclude = self._get_validation_exclusions()

        email = self.cleaned_data.get("email")
        phone = self.cleaned_data.get("phone")

        if not email:
            exclude.add("email")
            self.instance.email = None

        if not phone:
            exclude.add("phone")
            self.instance.phone = None

        try:
            self.instance.validate_unique(
                exclude=exclude
            )
        except ValidationError as error:
            self._update_errors(error)


class AdminUserChangeForm(
    OptionalContactFieldsMixin,
    UserChangeForm,
):
    """نموذج تعديل المستخدم داخل الإدارة."""

    class Meta(UserChangeForm.Meta):
        model = User


class AdminUserCreationForm(
    OptionalContactFieldsMixin,
    UserCreationForm,
):
    """نموذج إنشاء المستخدم داخل الإدارة."""

    class Meta(UserCreationForm.Meta):
        model = User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    form = AdminUserChangeForm
    add_form = AdminUserCreationForm

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
        return (
            obj.get_full_name().strip()
            or obj.username
        )


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