from django import forms
from django.core.validators import (
    MaxValueValidator,
    MinValueValidator,
)

from academics.models import TeachingAssignment
from portfolios.models import Portfolio

from .models import Badge, Rubric


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

    def __init__(
        self,
        *args,
        teacher=None,
        subject=None,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)

        rubrics = Rubric.objects.filter(
            is_active=True
        )

        if subject is not None:
            rubrics = rubrics.filter(
                subject=subject
            )

        if (
            teacher is not None
            and not teacher.is_superuser
        ):
            rubrics = rubrics.filter(
                created_by=teacher
            )

        self.fields["rubric"].queryset = (
            rubrics.order_by("title")
        )


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

        self.fields[
            "general_feedback"
        ].required = True

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


class PortfolioChoiceField(
    forms.ModelChoiceField
):
    """عرض اسم الطالبة وفصلها في قائمة الاختيار."""

    def label_from_instance(self, portfolio):
        student_name = (
            portfolio.student.get_full_name()
            or portfolio.student.username
        )

        return (
            f"{student_name} — "
            f"{portfolio.classroom}"
        )


class BadgeAwardForm(forms.Form):
    """نموذج منح شارة لطالبة من لوحة المعلمة."""

    portfolio = PortfolioChoiceField(
        label="الطالبة",
        queryset=Portfolio.objects.none(),
        empty_label="اختاري الطالبة",
        widget=forms.Select(
            attrs={"class": "form-control"}
        ),
    )

    badge = forms.ModelChoiceField(
        label="الشارة",
        queryset=Badge.objects.none(),
        empty_label="اختاري الشارة",
        widget=forms.Select(
            attrs={"class": "form-control"}
        ),
    )

    reason = forms.CharField(
        label="سبب منح الشارة",
        required=True,
        max_length=500,
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "rows": 4,
                "maxlength": "500",
                "placeholder": (
                    "اكتبي سبب منح الشارة للطالبة..."
                ),
            }
        ),
    )

    def __init__(
        self,
        *args,
        teacher=None,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)

        portfolios = (
            Portfolio.objects.filter(
                is_active=True,
                student__is_active=True,
            )
            .select_related(
                "student",
                "classroom",
                "classroom__grade_level",
            )
        )

        if (
            teacher is not None
            and not teacher.is_superuser
        ):
            classroom_ids = (
                TeachingAssignment.objects.filter(
                    teacher=teacher,
                    is_active=True,
                )
                .values_list(
                    "classroom_id",
                    flat=True,
                )
            )

            portfolios = portfolios.filter(
                classroom_id__in=classroom_ids
            )

        self.fields["portfolio"].queryset = (
            portfolios.order_by(
                "classroom__grade_level__order",
                "classroom__name",
                "student__first_name",
                "student__last_name",
                "student__username",
            )
        )

        self.fields["badge"].queryset = (
            Badge.objects.filter(
                is_active=True
            ).order_by("name")
        )