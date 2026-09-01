from django import forms
from django.core.validators import FileExtensionValidator

from .models import (
    ALLOWED_PORTFOLIO_EXTENSIONS,
    Attachment,
    PortfolioSection,
    validate_portfolio_file_size,
)


class StudentSubmissionForm(forms.Form):
    """نموذج رفع عمل جديد إلى دفتر الطالبة."""

    title = forms.CharField(
        label="عنوان العمل",
        max_length=200,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "مثال: مطوية تصنيف المخلوقات الحية",
                "autocomplete": "off",
            }
        ),
    )

    description = forms.CharField(
        label="وصف العمل",
        required=False,
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "rows": 4,
                "placeholder": "اكتبي وصفًا مختصرًا للعمل...",
            }
        ),
    )

    section = forms.ModelChoiceField(
        label="قسم الدفتر",
        queryset=PortfolioSection.objects.none(),
        required=False,
        empty_label="بدون قسم محدد",
        widget=forms.Select(
            attrs={
                "class": "form-control",
            }
        ),
    )

    file = forms.FileField(
        label="اختيار الملف",
        validators=[
            FileExtensionValidator(
                allowed_extensions=ALLOWED_PORTFOLIO_EXTENSIONS
            ),
            validate_portfolio_file_size,
        ],
        widget=forms.ClearableFileInput(
            attrs={
                "class": "form-control",
                "accept": (
                    ".pdf,.doc,.docx,.ppt,.pptx,.xls,.xlsx,"
                    ".jpg,.jpeg,.png,.webp,.mp4,.mov,.webm,"
                    ".mp3,.wav,.m4a"
                ),
            }
        ),
        help_text=(
            "يمكن رفع صورة أو PDF أو Word أو PowerPoint أو Excel "
            "أو فيديو مدته المقترحة من دقيقة إلى دقيقتين "
            "أو تسجيل صوتي، بحد أقصى 100 ميجابايت."
        ),
    )

    media_type = forms.ChoiceField(
        label="نوع العمل",
        choices=Attachment.MediaType.choices,
        widget=forms.Select(
            attrs={
                "class": "form-control",
            }
        ),
    )

    caption = forms.CharField(
        label="وصف الملف",
        max_length=255,
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "وصف مختصر للملف المرفوع",
            }
        ),
    )

    reflection = forms.CharField(
        label="ماذا تعلمت من هذا العمل؟",
        required=False,
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "rows": 3,
                "placeholder": "اكتبي تأملك العلمي وما تعلمته...",
            }
        ),
    )

    ai_used = forms.BooleanField(
        label="استخدمت الذكاء الاصطناعي في إعداد العمل",
        required=False,
    )

    ai_tools = forms.CharField(
        label="أداة الذكاء الاصطناعي المستخدمة",
        max_length=255,
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "مثال: ChatGPT أو Canva",
            }
        ),
    )

    ai_usage_description = forms.CharField(
        label="كيف استخدمت الذكاء الاصطناعي؟",
        required=False,
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "rows": 3,
                "placeholder": "وضحي كيف ساعدك الذكاء الاصطناعي...",
            }
        ),
    )

    def __init__(self, *args, portfolio=None, **kwargs):
        super().__init__(*args, **kwargs)

        if portfolio is not None:
            self.fields["section"].queryset = (
                PortfolioSection.objects.filter(
                    portfolio=portfolio
                ).order_by("order")
            )

    def clean(self):
        cleaned_data = super().clean()

        ai_used = cleaned_data.get("ai_used")
        ai_tools = cleaned_data.get("ai_tools", "").strip()
        ai_usage_description = cleaned_data.get(
            "ai_usage_description",
            "",
        ).strip()

        if ai_used and not ai_tools:
            self.add_error(
                "ai_tools",
                "اكتبي اسم أداة الذكاء الاصطناعي المستخدمة.",
            )

        if ai_used and not ai_usage_description:
            self.add_error(
                "ai_usage_description",
                "وضحي باختصار كيف استخدمتِ الذكاء الاصطناعي.",
            )

        return cleaned_data
