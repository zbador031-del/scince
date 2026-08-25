from django import forms
from django.core.exceptions import ValidationError

from academics.models import (
    Classroom,
    Lesson,
    Subject,
    TeachingAssignment,
    Term,
    Unit,
)

from .models import Activity


class ActivityForm(forms.ModelForm):
    """نموذج إنشاء وتعديل نشاط تعليمي."""

    classrooms = forms.ModelMultipleChoiceField(
        label="الفصول المستهدفة",
        queryset=Classroom.objects.none(),
        widget=forms.CheckboxSelectMultiple(),
        help_text=(
            "يمكن اختيار فصل واحد أو عدة فصول."
        ),
    )

    class Meta:
        model = Activity

        fields = [
            "title",
            "description",
            "instructions",
            "activity_type",
            "work_mode",
            "ai_policy",
            "subject",
            "unit",
            "lesson",
            "term",
            "classrooms",
            "max_score",
            "opens_at",
            "due_at",
            "allow_late_submission",
            "max_files",
            "max_file_size_mb",
            "reference_file",
            "is_published",
        ]

        widgets = {
            "title": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": (
                        "مثال: مطوية تصنيف المخلوقات الحية"
                    ),
                }
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "وصف مختصر للنشاط",
                }
            ),
            "instructions": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 5,
                    "placeholder": (
                        "اكتبي خطوات التنفيذ والمتطلبات..."
                    ),
                }
            ),
            "activity_type": forms.Select(
                attrs={"class": "form-control"}
            ),
            "work_mode": forms.Select(
                attrs={"class": "form-control"}
            ),
            "ai_policy": forms.Select(
                attrs={"class": "form-control"}
            ),
            "subject": forms.Select(
                attrs={"class": "form-control"}
            ),
            "unit": forms.Select(
                attrs={"class": "form-control"}
            ),
            "lesson": forms.Select(
                attrs={"class": "form-control"}
            ),
            "term": forms.Select(
                attrs={"class": "form-control"}
            ),
            "max_score": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": "0",
                    "step": "0.5",
                }
            ),
            "opens_at": forms.DateTimeInput(
                attrs={
                    "class": "form-control",
                    "type": "datetime-local",
                },
                format="%Y-%m-%dT%H:%M",
            ),
            "due_at": forms.DateTimeInput(
                attrs={
                    "class": "form-control",
                    "type": "datetime-local",
                },
                format="%Y-%m-%dT%H:%M",
            ),
            "max_files": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": "1",
                    "max": "10",
                }
            ),
            "max_file_size_mb": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": "1",
                    "max": "500",
                }
            ),
            "reference_file": forms.ClearableFileInput(
                attrs={"class": "form-control"}
            ),
        }

    def __init__(self, *args, teacher=None, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["opens_at"].input_formats = [
            "%Y-%m-%dT%H:%M"
        ]

        self.fields["due_at"].input_formats = [
            "%Y-%m-%dT%H:%M"
        ]

        self.fields["unit"].queryset = (
            Unit.objects.select_related(
                "subject",
                "grade_level",
                "term",
            ).order_by(
                "grade_level__order",
                "term__number",
                "order",
            )
        )

        self.fields["lesson"].queryset = (
            Lesson.objects.select_related(
                "unit"
            ).filter(
                is_active=True
            ).order_by(
                "unit__order",
                "order",
            )
        )

        self.fields["term"].queryset = (
            Term.objects.select_related(
                "academic_year"
            ).order_by(
                "-academic_year__start_date",
                "number",
            )
        )

        if teacher is None:
            self.fields["classrooms"].queryset = (
                Classroom.objects.none()
            )
            self.fields["subject"].queryset = (
                Subject.objects.none()
            )
            return

        if teacher.is_superuser:
            self.fields["classrooms"].queryset = (
                Classroom.objects.filter(
                    is_active=True
                ).select_related(
                    "grade_level"
                ).order_by(
                    "grade_level__order",
                    "name",
                )
            )

            self.fields["subject"].queryset = (
                Subject.objects.filter(
                    is_active=True
                ).order_by("name")
            )
        else:
            assignments = TeachingAssignment.objects.filter(
                teacher=teacher,
                is_active=True,
            )

            self.fields["classrooms"].queryset = (
                Classroom.objects.filter(
                    teaching_assignments__in=assignments,
                    is_active=True,
                )
                .select_related("grade_level")
                .distinct()
                .order_by(
                    "grade_level__order",
                    "name",
                )
            )

            self.fields["subject"].queryset = (
                Subject.objects.filter(
                    teaching_assignments__in=assignments,
                    is_active=True,
                )
                .distinct()
                .order_by("name")
            )

        if self.instance.pk:
            self.fields["classrooms"].initial = (
                self.instance.classrooms.all()
            )

    def clean(self):
        cleaned_data = super().clean()

        subject = cleaned_data.get("subject")
        unit = cleaned_data.get("unit")
        lesson = cleaned_data.get("lesson")
        opens_at = cleaned_data.get("opens_at")
        due_at = cleaned_data.get("due_at")

        if unit and subject and unit.subject_id != subject.id:
            self.add_error(
                "unit",
                "الوحدة المختارة لا تتبع المقرر المحدد.",
            )

        if lesson and unit and lesson.unit_id != unit.id:
            self.add_error(
                "lesson",
                "الدرس المختار لا يتبع الوحدة المحددة.",
            )

        if lesson and not unit:
            self.add_error(
                "unit",
                "اختاري الوحدة المرتبطة بالدرس.",
            )

        if opens_at and due_at and opens_at > due_at:
            raise ValidationError(
                "موعد بداية النشاط يجب أن يسبق موعد التسليم."
            )

        return cleaned_data