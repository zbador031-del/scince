from django import forms
from django.core.validators import (
    MaxValueValidator,
    MinValueValidator,
)

from .models import Rubric


class EvaluationDecision:
    DRAFT = "draft"
    APPROVED = "approved"
    REVISION_REQUIRED = "revision_required"
    FEATURED = "featured"

    CHOICES = [
        (DRAFT, "حفظ التقييم مسودة"),
        (APPROVED, "اعتماد العمل"),
        (REVISION_REQUIRED, "طلب تعديل العمل"),
        (FEATURED, "اعتماد العمل وتصنيفه متميزًا"),
    ]


class EvaluationForm(forms.Form):
    """نموذج تقييم عمل طالبة واحدة."""

    rubric = forms.ModelChoiceField(
        label="سلم التقدير",
        queryset=Rubric.objects.none(),
        empty_label="اختاري سلم التقدير",
        widget=forms.Select(
            attrs={"class": "form-control"}
        ),
    )

    total_score = forms.DecimalField(
        label="الدرجة من 20",
        max_digits=5,
        decimal_places=2,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(20),
        ],
        widget=forms.NumberInput(
            attrs={
                "class": "form-control",
                "min": "0",
                "max": "20",
                "step": "0.5",
                "placeholder": "مثال: 18",
            }
        ),
    )

    general_feedback = forms.CharField(
        label="التغذية الراجعة",
        required=False,
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "rows": 5,
                "placeholder": (
                    "اكتبي نقاط القوة وما يحتاج إلى تحسين..."
                ),
            }
        ),
    )

    decision = forms.ChoiceField(
        label="قرار التقييم",
        choices=EvaluationDecision.CHOICES,
        widget=forms.Select(
            attrs={"class": "form-control"}
        ),
    )

    def __init__(self, *args, teacher=None, subject=None, **kwargs):
        super().__init__(*args, **kwargs)

        rubrics = Rubric.objects.filter(is_active=True)

        if subject is not None:
            rubrics = rubrics.filter(subject=subject)

        if teacher is not None and not teacher.is_superuser:
            rubrics = rubrics.filter(created_by=teacher)

        self.fields["rubric"].queryset = rubrics.order_by("title")


class BulkEvaluationForm(EvaluationForm):
    """نموذج تطبيق تقييم موحد على عدة أعمال."""

    confirm = forms.BooleanField(
        label=(
            "أؤكد تطبيق الدرجة والتغذية الراجعة "
            "على جميع الأعمال المحددة"
        ),
        required=True,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["general_feedback"].required = True
        self.fields["decision"].choices = [
            (
                EvaluationDecision.APPROVED,
                "اعتماد جميع الأعمال المحددة",
            ),
            (
                EvaluationDecision.REVISION_REQUIRED,
                "طلب تعديل جميع الأعمال المحددة",
            ),
            (
                EvaluationDecision.FEATURED,
                "اعتماد الأعمال وتصنيفها متميزة",
            ),
        ]