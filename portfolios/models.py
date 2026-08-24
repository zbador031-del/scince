from pathlib import Path

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from django.db import models
from django.db.models import Q


ALLOWED_PORTFOLIO_EXTENSIONS = [
    "pdf",
    "doc",
    "docx",
    "ppt",
    "pptx",
    "xls",
    "xlsx",
    "jpg",
    "jpeg",
    "png",
    "webp",
    "mp4",
    "mov",
    "webm",
    "mp3",
    "wav",
    "m4a",
]


def validate_portfolio_file_size(uploaded_file):
    """منع رفع ملف يتجاوز 100 ميجابايت."""

    maximum_size = 100 * 1024 * 1024

    if uploaded_file.size > maximum_size:
        raise ValidationError(
            "حجم الملف يتجاوز الحد الأعلى المسموح وهو 100 ميجابايت."
        )


class Portfolio(models.Model):
    """دفتر العلوم الرقمي الخاص بالطالبة."""

    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="portfolios",
        limit_choices_to={"role": "student"},
        verbose_name="الطالبة",
    )

    classroom = models.ForeignKey(
        "academics.Classroom",
        on_delete=models.CASCADE,
        related_name="portfolios",
        verbose_name="الشعبة",
    )

    subject = models.ForeignKey(
        "academics.Subject",
        on_delete=models.CASCADE,
        related_name="portfolios",
        verbose_name="المقرر",
    )

    academic_year = models.ForeignKey(
        "academics.AcademicYear",
        on_delete=models.CASCADE,
        related_name="portfolios",
        verbose_name="العام الدراسي",
    )

    title = models.CharField(
        "عنوان الدفتر",
        max_length=200,
        default="دفتر العلوم الذكي",
    )

    introduction = models.TextField(
        "نبذة الطالبة",
        blank=True,
    )

    learning_goals = models.TextField(
        "أهداف التعلم",
        blank=True,
    )

    cover_image = models.ImageField(
        "صورة الغلاف",
        upload_to="portfolios/covers/",
        null=True,
        blank=True,
    )

    is_active = models.BooleanField(
        "دفتر نشط",
        default=True,
    )

    created_at = models.DateTimeField(
        "تاريخ الإنشاء",
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        "آخر تحديث",
        auto_now=True,
    )

    class Meta:
        verbose_name = "دفتر طالبة"
        verbose_name_plural = "دفاتر الطالبات"
        ordering = ["student__first_name"]
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "student",
                    "classroom",
                    "subject",
                    "academic_year",
                ],
                name="unique_student_portfolio",
            )
        ]

    def __str__(self):
        return f"{self.title} - {self.student}"


class PortfolioSection(models.Model):
    """قسم داخل دفتر الطالبة."""

    portfolio = models.ForeignKey(
        Portfolio,
        on_delete=models.CASCADE,
        related_name="sections",
        verbose_name="الدفتر",
    )

    unit = models.ForeignKey(
        "academics.Unit",
        on_delete=models.SET_NULL,
        related_name="portfolio_sections",
        null=True,
        blank=True,
        verbose_name="الوحدة",
    )

    title = models.CharField(
        "عنوان القسم",
        max_length=200,
    )

    description = models.TextField(
        "وصف القسم",
        blank=True,
    )

    order = models.PositiveSmallIntegerField(
        "الترتيب",
        default=1,
    )

    class Meta:
        verbose_name = "قسم دفتر"
        verbose_name_plural = "أقسام الدفاتر"
        ordering = ["portfolio", "order"]
        constraints = [
            models.UniqueConstraint(
                fields=["portfolio", "order"],
                name="unique_portfolio_section_order",
            )
        ]

    def __str__(self):
        return self.title


class Submission(models.Model):
    """العمل الأساسي الذي تضيفه الطالبة إلى دفترها."""

    class Status(models.TextChoices):
        DRAFT = "draft", "مسودة"
        SUBMITTED = "submitted", "تم التسليم"
        UNDER_REVIEW = "under_review", "قيد التقييم"
        REVISION_REQUIRED = "revision_required", "يحتاج تعديلًا"
        RESUBMITTED = "resubmitted", "أعيد التسليم"
        APPROVED = "approved", "تم الاعتماد"
        FEATURED = "featured", "عمل متميز"

    portfolio = models.ForeignKey(
        Portfolio,
        on_delete=models.CASCADE,
        related_name="submissions",
        verbose_name="دفتر الطالبة",
    )

    activity = models.ForeignKey(
        "activities.Activity",
        on_delete=models.SET_NULL,
        related_name="submissions",
        null=True,
        blank=True,
        verbose_name="النشاط المرتبط",
    )

    section = models.ForeignKey(
        PortfolioSection,
        on_delete=models.SET_NULL,
        related_name="submissions",
        null=True,
        blank=True,
        verbose_name="قسم الدفتر",
    )

    title = models.CharField(
        "عنوان العمل",
        max_length=200,
    )

    description = models.TextField(
        "وصف العمل",
        blank=True,
    )

    status = models.CharField(
        "حالة العمل",
        max_length=30,
        choices=Status.choices,
        default=Status.DRAFT,
        db_index=True,
    )

    collaborators = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="collaborative_submissions",
        blank=True,
        limit_choices_to={"role": "student"},
        verbose_name="الطالبات المشاركات",
    )

    is_featured = models.BooleanField(
        "عمل متميز",
        default=False,
    )

    submitted_at = models.DateTimeField(
        "تاريخ آخر تسليم",
        null=True,
        blank=True,
    )

    created_at = models.DateTimeField(
        "تاريخ الإنشاء",
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        "آخر تحديث",
        auto_now=True,
    )

    class Meta:
        verbose_name = "عمل طالبة"
        verbose_name_plural = "أعمال الطالبات"
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["portfolio", "activity"],
                condition=Q(activity__isnull=False),
                name="unique_portfolio_activity_submission",
            )
        ]

    def __str__(self):
        return f"{self.title} - {self.portfolio.student}"


class SubmissionVersion(models.Model):
    """نسخة من العمل لحفظ تطور الطالبة وإعادة التسليم."""

    submission = models.ForeignKey(
        Submission,
        on_delete=models.CASCADE,
        related_name="versions",
        verbose_name="العمل",
    )

    version_number = models.PositiveIntegerField(
        "رقم النسخة",
        default=1,
    )

    notes = models.TextField(
        "ملاحظات الطالبة",
        blank=True,
    )

    reflection = models.TextField(
        "التأمل الذاتي",
        blank=True,
        help_text="ماذا تعلمت الطالبة؟ وما الذي ستطوره؟",
    )

    ai_used = models.BooleanField(
        "تم استخدام الذكاء الاصطناعي",
        default=False,
    )

    ai_tools = models.CharField(
        "أدوات الذكاء الاصطناعي المستخدمة",
        max_length=255,
        blank=True,
    )

    ai_usage_description = models.TextField(
        "وصف استخدام الذكاء الاصطناعي",
        blank=True,
    )

    is_current = models.BooleanField(
        "النسخة الحالية",
        default=True,
    )

    submitted_at = models.DateTimeField(
        "تاريخ رفع النسخة",
        auto_now_add=True,
    )

    class Meta:
        verbose_name = "نسخة عمل"
        verbose_name_plural = "نسخ الأعمال"
        ordering = ["submission", "-version_number"]
        constraints = [
            models.UniqueConstraint(
                fields=["submission", "version_number"],
                name="unique_submission_version",
            )
        ]

    def __str__(self):
        return f"{self.submission} - النسخة {self.version_number}"


class Attachment(models.Model):
    """ملف أو صورة أو فيديو مرفق بنسخة العمل."""

    class MediaType(models.TextChoices):
        DOCUMENT = "document", "مستند"
        IMAGE = "image", "صورة"
        VIDEO = "video", "فيديو"
        AUDIO = "audio", "تسجيل صوتي"
        PRESENTATION = "presentation", "عرض تقديمي"
        OTHER = "other", "ملف آخر"

    version = models.ForeignKey(
        SubmissionVersion,
        on_delete=models.CASCADE,
        related_name="attachments",
        verbose_name="نسخة العمل",
    )

    file = models.FileField(
        "الملف",
        upload_to="portfolios/submissions/%Y/%m/",
        validators=[
            FileExtensionValidator(
                allowed_extensions=ALLOWED_PORTFOLIO_EXTENSIONS
            ),
            validate_portfolio_file_size,
        ],
    )

    media_type = models.CharField(
        "نوع الملف",
        max_length=20,
        choices=MediaType.choices,
        default=MediaType.DOCUMENT,
    )

    caption = models.CharField(
        "وصف الملف",
        max_length=255,
        blank=True,
    )

    original_filename = models.CharField(
        "اسم الملف الأصلي",
        max_length=255,
        blank=True,
    )

    mime_type = models.CharField(
        "نوع محتوى الملف",
        max_length=100,
        blank=True,
    )

    size_bytes = models.PositiveBigIntegerField(
        "حجم الملف بالبايت",
        default=0,
    )

    uploaded_at = models.DateTimeField(
        "تاريخ الرفع",
        auto_now_add=True,
    )

    class Meta:
        verbose_name = "مرفق"
        verbose_name_plural = "المرفقات"
        ordering = ["uploaded_at"]

    def save(self, *args, **kwargs):
        if self.file:
            if not self.original_filename:
                self.original_filename = Path(self.file.name).name

            try:
                self.size_bytes = self.file.size
            except (AttributeError, OSError):
                pass

        super().save(*args, **kwargs)

    def __str__(self):
        return self.original_filename or Path(self.file.name).name


class SubmissionComment(models.Model):
    """مناقشة وتعليقات مرتبطة بالعمل."""

    submission = models.ForeignKey(
        Submission,
        on_delete=models.CASCADE,
        related_name="comments",
        verbose_name="العمل",
    )

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="submission_comments",
        verbose_name="كاتب التعليق",
    )

    body = models.TextField(
        "التعليق",
    )

    is_private = models.BooleanField(
        "تعليق خاص بالمعلمة",
        default=False,
    )

    created_at = models.DateTimeField(
        "تاريخ التعليق",
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        "آخر تعديل",
        auto_now=True,
    )

    class Meta:
        verbose_name = "تعليق على عمل"
        verbose_name_plural = "تعليقات الأعمال"
        ordering = ["created_at"]

    def __str__(self):
        return f"تعليق {self.author} على {self.submission}"