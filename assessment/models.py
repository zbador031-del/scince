from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models


class Rubric(models.Model):
    """سلم التقدير المستخدم في تقييم أعمال الطالبات."""

    title = models.CharField(
        "اسم سلم التقدير",
        max_length=200,
    )

    description = models.TextField(
        "وصف سلم التقدير",
        blank=True,
    )

    subject = models.ForeignKey(
        "academics.Subject",
        on_delete=models.CASCADE,
        related_name="rubrics",
        verbose_name="المقرر",
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="created_rubrics",
        limit_choices_to={"role": "teacher"},
        verbose_name="أنشئ بواسطة",
    )

    is_active = models.BooleanField(
        "نشط",
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
        verbose_name = "سلم تقدير"
        verbose_name_plural = "سلالم التقدير"
        ordering = ["title"]

    def __str__(self):
        return self.title

    @property
    def maximum_score(self):
        return sum(
            criterion.max_points
            for criterion in self.criteria.all()
        )


class RubricCriterion(models.Model):
    """معيار داخل سلم التقدير."""

    rubric = models.ForeignKey(
        Rubric,
        on_delete=models.CASCADE,
        related_name="criteria",
        verbose_name="سلم التقدير",
    )

    title = models.CharField(
        "عنوان المعيار",
        max_length=200,
    )

    description = models.TextField(
        "وصف المعيار",
        blank=True,
    )

    max_points = models.DecimalField(
        "الدرجة القصوى",
        max_digits=6,
        decimal_places=2,
        validators=[MinValueValidator(0)],
    )

    order = models.PositiveSmallIntegerField(
        "الترتيب",
        default=1,
    )

    class Meta:
        verbose_name = "معيار تقييم"
        verbose_name_plural = "معايير التقييم"
        ordering = ["rubric", "order"]
        constraints = [
            models.UniqueConstraint(
                fields=["rubric", "order"],
                name="unique_rubric_criterion_order",
            )
        ]

    def __str__(self):
        return self.title


class ActivityRubric(models.Model):
    """ربط النشاط بسلم التقدير المناسب."""

    activity = models.OneToOneField(
        "activities.Activity",
        on_delete=models.CASCADE,
        related_name="rubric_assignment",
        verbose_name="النشاط",
    )

    rubric = models.ForeignKey(
        Rubric,
        on_delete=models.PROTECT,
        related_name="activity_assignments",
        verbose_name="سلم التقدير",
    )

    assigned_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="rubric_assignments",
        verbose_name="تم الربط بواسطة",
    )

    assigned_at = models.DateTimeField(
        "تاريخ الربط",
        auto_now_add=True,
    )

    class Meta:
        verbose_name = "ربط نشاط بسلم تقدير"
        verbose_name_plural = "ربط الأنشطة بسلالم التقدير"

    def __str__(self):
        return f"{self.activity} - {self.rubric}"


class Evaluation(models.Model):
    """تقييم نسخة محددة من عمل الطالبة."""

    class Status(models.TextChoices):
        DRAFT = "draft", "مسودة"
        PUBLISHED = "published", "تم نشر التقييم"
        REVISION_REQUIRED = "revision_required", "يحتاج تعديلًا"

    submission_version = models.OneToOneField(
        "portfolios.SubmissionVersion",
        on_delete=models.CASCADE,
        related_name="evaluation",
        verbose_name="نسخة العمل",
    )

    evaluator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="evaluations",
        limit_choices_to={"role": "teacher"},
        verbose_name="المقيّمة",
    )

    rubric = models.ForeignKey(
        Rubric,
        on_delete=models.PROTECT,
        related_name="evaluations",
        verbose_name="سلم التقدير",
    )

    total_score = models.DecimalField(
        "الدرجة الكلية",
        max_digits=7,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0)],
    )

    general_feedback = models.TextField(
        "التغذية الراجعة",
        blank=True,
    )

    audio_feedback = models.FileField(
        "تغذية راجعة صوتية",
        upload_to="assessment/audio_feedback/",
        null=True,
        blank=True,
    )

    status = models.CharField(
        "حالة التقييم",
        max_length=30,
        choices=Status.choices,
        default=Status.DRAFT,
        db_index=True,
    )

    evaluated_at = models.DateTimeField(
        "تاريخ التقييم",
        auto_now=True,
    )

    published_at = models.DateTimeField(
        "تاريخ نشر التقييم",
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = "تقييم"
        verbose_name_plural = "التقييمات"
        ordering = ["-evaluated_at"]

    def __str__(self):
        return f"تقييم {self.submission_version}"


class CriterionScore(models.Model):
    """درجة معيار محدد داخل التقييم."""

    evaluation = models.ForeignKey(
        Evaluation,
        on_delete=models.CASCADE,
        related_name="criterion_scores",
        verbose_name="التقييم",
    )

    criterion = models.ForeignKey(
        RubricCriterion,
        on_delete=models.PROTECT,
        related_name="scores",
        verbose_name="المعيار",
    )

    score = models.DecimalField(
        "الدرجة",
        max_digits=6,
        decimal_places=2,
        validators=[MinValueValidator(0)],
    )

    feedback = models.TextField(
        "ملاحظة المعيار",
        blank=True,
    )

    class Meta:
        verbose_name = "درجة معيار"
        verbose_name_plural = "درجات المعايير"
        constraints = [
            models.UniqueConstraint(
                fields=["evaluation", "criterion"],
                name="unique_evaluation_criterion_score",
            )
        ]

    def __str__(self):
        return f"{self.criterion}: {self.score}"


class Badge(models.Model):
    """شارة تحفيزية تمنح للطالبة."""

    name = models.CharField(
        "اسم الشارة",
        max_length=100,
        unique=True,
    )

    description = models.TextField(
        "وصف الشارة",
        blank=True,
    )

    icon = models.ImageField(
        "أيقونة الشارة",
        upload_to="assessment/badges/",
        null=True,
        blank=True,
    )

    color = models.CharField(
        "لون الشارة",
        max_length=20,
        default="#C59D4F",
    )

    is_active = models.BooleanField(
        "شارة نشطة",
        default=True,
    )

    class Meta:
        verbose_name = "شارة"
        verbose_name_plural = "الشارات"
        ordering = ["name"]

    def __str__(self):
        return self.name


class StudentBadge(models.Model):
    """شارة حصلت عليها الطالبة داخل دفترها."""

    portfolio = models.ForeignKey(
        "portfolios.Portfolio",
        on_delete=models.CASCADE,
        related_name="earned_badges",
        verbose_name="دفتر الطالبة",
    )

    badge = models.ForeignKey(
        Badge,
        on_delete=models.CASCADE,
        related_name="awards",
        verbose_name="الشارة",
    )

    submission = models.ForeignKey(
        "portfolios.Submission",
        on_delete=models.SET_NULL,
        related_name="awarded_badges",
        null=True,
        blank=True,
        verbose_name="العمل المرتبط",
    )

    awarded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="awarded_badges",
        verbose_name="منحت بواسطة",
    )

    reason = models.TextField(
        "سبب منح الشارة",
        blank=True,
    )

    awarded_at = models.DateTimeField(
        "تاريخ المنح",
        auto_now_add=True,
    )

    class Meta:
        verbose_name = "شارة طالبة"
        verbose_name_plural = "شارات الطالبات"
        ordering = ["-awarded_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["portfolio", "badge", "submission"],
                name="unique_portfolio_badge_submission",
            )
        ]

    def __str__(self):
        return f"{self.badge} - {self.portfolio.student}"