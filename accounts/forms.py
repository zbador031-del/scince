from django import forms

from academics.models import Classroom


class BulkStudentAccountForm(forms.Form):
    """نموذج إنشاء حسابات الطالبات جماعيًا."""

    classroom = forms.ModelChoiceField(
        label="الشعبة",
        queryset=Classroom.objects.none(),
        empty_label="اختاري الصف والشعبة",
        widget=forms.Select(
            attrs={
                "class": "form-control",
            }
        ),
    )

    student_count = forms.IntegerField(
        label="إجمالي عدد طالبات الشعبة",
        min_value=1,
        max_value=60,
        help_text=(
            "أدخلي العدد الإجمالي المطلوب في الشعبة، "
            "وسيُنشئ النظام الحسابات الناقصة فقط."
        ),
        widget=forms.NumberInput(
            attrs={
                "class": "form-control",
                "placeholder": "مثال: 26",
            }
        ),
    )

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)

        classrooms = Classroom.objects.filter(
            is_active=True,
        ).select_related(
            "grade_level",
            "academic_year",
            "school",
        )

        if user and not user.is_superuser:
            classrooms = classrooms.filter(
                teaching_assignments__teacher=user,
                teaching_assignments__is_active=True,
            ).distinct()

        self.fields["classroom"].queryset = classrooms.order_by(
            "grade_level__order",
            "name",
        )