from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import (
    MaxValueValidator,
    MinValueValidator,
)
from django.db import models


class AIAnalysis(models.Model):
    """نتيجة تحليل عمل الطالبة باستخدام الذكاء الاصطناعي."""

    class Status(models.TextChoices):
        PENDING = "pending", "في الانتظار"
        PROCESSING = "processing", "قيد التحليل"
        COMPLETED = "completed", "اكتمل التحليل"
        FAILED = "failed", "فشل التحليل"

    submission_version = models.OneToOneField(
        "portfolios.SubmissionVersion",
        on_delete=models.CASCADE,
        related_name="ai_analysis",
        verbose_name="نسخة العمل",
    )

    requested_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="requested_ai_analyses",
        null=True,
        blank=True,
        verbose_name="طلب التحليل بواسطة",
    )

    status = models.CharField(
        "حالة التحليل",
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        db_index=True,
    )

    summary = models.TextField(
        "ملخص العمل",
        blank=True,
    )

    scientific_concepts = models.JSONField(
        "المفاهيم العلمية",
        default=list,
        blank=True,
    )

    strengths = models.JSONField(
        "نقاط القوة",
        default=list,
        blank=True,
    )

    improvement_areas = models.JSONField(
        "جوانب التحسين",
        default=list,
        blank=True,
    )

    missing_requirements = models.JSONField(
        "المتطلبات الناقصة",
        default=list,
        blank=True,
    )

    suggested_feedback = models.TextField(
        "التغذية الراجعة المقترحة",
        blank=True,
    )

    suggested_score = models.DecimalField(
        "الدرجة المقترحة",
        max_digits=7,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[
            MinValueValidator(0),
        ],
    )

    confidence_score = models.DecimalField(
        "درجة الثقة",
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(100),
        ],
    )

    provider_name = models.CharField(
        "مزود الذكاء الاصطناعي",
        max_length=100,
        blank=True,
    )

    model_name = models.CharField(
        "اسم النموذج",
        max_length=100,
        blank=True,
    )

    error_message = models.TextField(
        "رسالة الخطأ",
        blank=True,
    )

    created_at = models.DateTimeField(
        "تاريخ طلب التحليل",
        auto_now_add=True,
    )

    completed_at = models.DateTimeField(
        "تاريخ اكتمال التحليل",
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = "تحليل ذكي"
        verbose_name_plural = "التحليلات الذكية"
        ordering = ["-created_at"]

    def __str__(self):
        return f"تحليل {self.submission_version}"


class AIUsageLog(models.Model):
    """سجل استخدام خدمات الذكاء الاصطناعي."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="ai_usage_logs",
        null=True,
        blank=True,
        verbose_name="المستخدم",
    )

    feature_name = models.CharField(
        "الخاصية المستخدمة",
        max_length=100,
    )

    provider_name = models.CharField(
        "مزود الخدمة",
        max_length=100,
        blank=True,
    )

    model_name = models.CharField(
        "اسم النموذج",
        max_length=100,
        blank=True,
    )

    input_tokens = models.PositiveIntegerField(
        "رموز الإدخال",
        default=0,
    )

    output_tokens = models.PositiveIntegerField(
        "رموز الإخراج",
        default=0,
    )

    duration_ms = models.PositiveIntegerField(
        "مدة التنفيذ بالمللي ثانية",
        default=0,
    )

    was_successful = models.BooleanField(
        "تمت العملية بنجاح",
        default=True,
    )

    error_code = models.CharField(
        "رمز الخطأ",
        max_length=100,
        blank=True,
    )

    created_at = models.DateTimeField(
        "تاريخ الاستخدام",
        auto_now_add=True,
        db_index=True,
    )

    class Meta:
        verbose_name = "سجل استخدام ذكي"
        verbose_name_plural = "سجلات الاستخدام الذكي"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.feature_name} - {self.created_at}"


class PerformanceSnapshot(models.Model):
    """لقطة دورية لمؤشرات أداء دفتر الطالبة."""

    class RiskLevel(models.TextChoices):
        LOW = "low", "مستقرة"
        MEDIUM = "medium", "تحتاج متابعة"
        HIGH = "high", "تحتاج تدخلًا"

    portfolio = models.ForeignKey(
        "portfolios.Portfolio",
        on_delete=models.CASCADE,
        related_name="performance_snapshots",
        verbose_name="دفتر الطالبة",
    )

    term = models.ForeignKey(
        "academics.Term",
        on_delete=models.CASCADE,
        related_name="performance_snapshots",
        verbose_name="الفصل الدراسي",
    )

    total_activities = models.PositiveIntegerField(
        "إجمالي الأنشطة",
        default=0,
    )

    submitted_activities = models.PositiveIntegerField(
        "الأنشطة المسلمة",
        default=0,
    )

    approved_activities = models.PositiveIntegerField(
        "الأنشطة المعتمدة",
        default=0,
    )

    late_activities = models.PositiveIntegerField(
        "الأنشطة المتأخرة",
        default=0,
    )

    completion_rate = models.DecimalField(
        "نسبة الإنجاز",
        max_digits=5,
        decimal_places=2,
        default=0,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(100),
        ],
    )

    average_score = models.DecimalField(
        "متوسط الدرجات",
        max_digits=7,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[
            MinValueValidator(0),
        ],
    )

    risk_level = models.CharField(
        "مستوى الاحتياج للمتابعة",
        max_length=20,
        choices=RiskLevel.choices,
        default=RiskLevel.LOW,
        db_index=True,
    )

    insights = models.JSONField(
        "المؤشرات والاستنتاجات",
        default=list,
        blank=True,
    )

    generated_at = models.DateTimeField(
        "تاريخ إنشاء المؤشرات",
        auto_now_add=True,
    )

    class Meta:
        verbose_name = "لقطة أداء"
        verbose_name_plural = "لقطات الأداء"
        ordering = ["-generated_at"]

    def __str__(self):
        return (
            f"{self.portfolio.student} - "
            f"{self.generated_at}"
        )


class Recommendation(models.Model):
    """توصية علاجية أو إثرائية للطالبة."""

    class RecommendationType(models.TextChoices):
        REMEDIAL = "remedial", "علاجية"
        ENRICHMENT = "enrichment", "إثرائية"
        MOTIVATIONAL = "motivational", "تحفيزية"
        ORGANIZATIONAL = "organizational", "تنظيمية"

    class Status(models.TextChoices):
        NEW = "new", "جديدة"
        SHARED = "shared", "تمت مشاركتها"
        COMPLETED = "completed", "تم تنفيذها"
        DISMISSED = "dismissed", "تم استبعادها"

    portfolio = models.ForeignKey(
        "portfolios.Portfolio",
        on_delete=models.CASCADE,
        related_name="recommendations",
        verbose_name="دفتر الطالبة",
    )

    lesson = models.ForeignKey(
        "academics.Lesson",
        on_delete=models.SET_NULL,
        related_name="recommendations",
        null=True,
        blank=True,
        verbose_name="الدرس",
    )

    recommendation_type = models.CharField(
        "نوع التوصية",
        max_length=20,
        choices=RecommendationType.choices,
    )

    title = models.CharField(
        "عنوان التوصية",
        max_length=200,
    )

    description = models.TextField(
        "تفاصيل التوصية",
    )

    resource_url = models.URLField(
        "رابط المورد التعليمي",
        blank=True,
    )

    priority = models.PositiveSmallIntegerField(
        "الأولوية",
        default=1,
    )

    status = models.CharField(
        "حالة التوصية",
        max_length=20,
        choices=Status.choices,
        default=Status.NEW,
    )

    created_by_ai = models.BooleanField(
        "تم إنشاؤها بالذكاء الاصطناعي",
        default=True,
    )

    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="reviewed_recommendations",
        null=True,
        blank=True,
        verbose_name="راجعتها المعلمة",
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
        verbose_name = "توصية"
        verbose_name_plural = "التوصيات"
        ordering = ["priority", "-created_at"]

    def __str__(self):
        return self.title


class MonthlyHonor(models.Model):
    """سجل عالمة الشهر والشريط والتقرير الشهري."""

    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="monthly_honors",
        limit_choices_to={"role": "student"},
        verbose_name="الطالبة المكرمة",
    )

    classroom = models.ForeignKey(
        "academics.Classroom",
        on_delete=models.PROTECT,
        related_name="monthly_honors",
        verbose_name="الفصل",
    )

    month_start = models.DateField(
        "بداية الشهر",
        unique=True,
    )

    month_end = models.DateField(
        "نهاية الشهر",
    )

    hijri_month_label = models.CharField(
        "اسم الشهر الهجري",
        max_length=100,
        help_text="مثال: ربيع الأول 1448هـ",
    )

    average_score = models.DecimalField(
        "متوسط التقييم من 20",
        max_digits=5,
        decimal_places=2,
        default=0,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(20),
        ],
    )

    completion_rate = models.DecimalField(
        "نسبة إنجاز الأنشطة",
        max_digits=5,
        decimal_places=2,
        default=0,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(100),
        ],
    )

    improvement_rate = models.DecimalField(
        "نسبة التحسن",
        max_digits=6,
        decimal_places=2,
        default=0,
        validators=[
            MinValueValidator(-100),
            MaxValueValidator(100),
        ],
    )

    submitted_activities = models.PositiveIntegerField(
        "عدد الأنشطة المسلمة",
        default=0,
    )

    approved_activities = models.PositiveIntegerField(
        "عدد الأعمال المعتمدة",
        default=0,
    )

    featured_activities = models.PositiveIntegerField(
        "عدد الأعمال المتميزة",
        default=0,
    )

    featured_submission = models.ForeignKey(
        "portfolios.Submission",
        on_delete=models.SET_NULL,
        related_name="monthly_honor_records",
        null=True,
        blank=True,
        verbose_name="أبرز عمل متميز",
    )

    selection_reason = models.TextField(
        "سبب اختيار الطالبة",
    )

    ticker_message = models.CharField(
        "رسالة الشريط المتحرك",
        max_length=300,
        blank=True,
        help_text=(
            "إذا تُركت فارغة سيُنشئ النظام عبارة افتراضية."
        ),
    )

    publish_student_name = models.BooleanField(
        "موافقة نشر الاسم الأول",
        default=False,
        help_text=(
            "عند عدم التفعيل سيظهر: طالبة متميزة."
        ),
    )

    is_approved = models.BooleanField(
        "معتمد",
        default=False,
        db_index=True,
    )

    is_active_in_ticker = models.BooleanField(
        "ظاهر في الشريط المتحرك",
        default=False,
        db_index=True,
    )

    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="approved_monthly_honors",
        null=True,
        blank=True,
        verbose_name="اعتمد بواسطة",
    )

    approved_at = models.DateTimeField(
        "تاريخ الاعتماد",
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
        verbose_name = "عالمة الشهر"
        verbose_name_plural = "عالمات الشهر"
        ordering = ["-month_start"]

    def clean(self):
        if self.month_end < self.month_start:
            raise ValidationError(
                "نهاية الشهر يجب أن تكون بعد بدايته."
            )

        if (
            self.is_active_in_ticker
            and not self.is_approved
        ):
            raise ValidationError(
                "يجب اعتماد التكريم قبل إظهاره في الشريط."
            )

        if (
            self.featured_submission
            and (
                self.featured_submission
                .portfolio.student_id
                != self.student_id
            )
        ):
            raise ValidationError(
                "العمل المتميز لا يتبع الطالبة المختارة."
            )

    @property
    def public_student_name(self):
        if self.publish_student_name:
            return (
                self.student.first_name
                or self.student.username
            )

        return "طالبة متميزة"

    @property
    def public_ticker_text(self):
        if self.ticker_message:
            return self.ticker_message

        return (
            f"عالمة الشهر: {self.public_student_name} "
            f"من {self.classroom} — "
            f"{self.selection_reason}"
        )

    def __str__(self):
        return (
            f"{self.hijri_month_label} - "
            f"{self.student}"
        )