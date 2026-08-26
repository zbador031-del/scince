from django.conf import settings
from django.db import models


class Activity(models.Model):
    """العمل أو النشاط الذي تطلبه المعلمة من الطالبات."""

    class ActivityType(models.TextChoices):
        WORKSHEET = "worksheet", "ورقة عمل"
        FOLDABLE = "foldable", "مطوية"
        EXPERIMENT = "experiment", "تجربة علمية"
        PROJECT = "project", "مشروع"
        REPORT = "report", "تقرير"
        PRESENTATION = "presentation", "عرض تقديمي"
        INFOGRAPHIC = "infographic", "إنفوجرافيك"
        CONCEPT_MAP = "concept_map", "خريطة مفاهيم"
        IMAGE = "image", "تصميم أو صورة"
        VIDEO = "video", "فيديو"
        AUDIO = "audio", "تسجيل صوتي"
        AI_WORK = "ai_work", "عمل بالذكاء الاصطناعي"
        OTHER = "other", "عمل آخر"

    class WorkMode(models.TextChoices):
        INDIVIDUAL = "individual", "فردي"
        GROUP = "group", "جماعي"

    class AIPolicy(models.TextChoices):
        NOT_ALLOWED = "not_allowed", "غير مسموح"
        OPTIONAL = "optional", "مسموح اختياريًا"
        REQUIRED = "required", "مطلوب"
        DISCLOSURE_REQUIRED = (
            "disclosure_required",
            "مسموح مع توضيح الاستخدام",
        )

    title = models.CharField(
        "عنوان النشاط",
        max_length=200,
    )

    description = models.TextField(
        "وصف النشاط",
        blank=True,
    )

    instructions = models.TextField(
        "تعليمات التنفيذ",
    )

    activity_type = models.CharField(
        "نوع النشاط",
        max_length=30,
        choices=ActivityType.choices,
        default=ActivityType.WORKSHEET,
        db_index=True,
    )

    work_mode = models.CharField(
        "طريقة التنفيذ",
        max_length=20,
        choices=WorkMode.choices,
        default=WorkMode.INDIVIDUAL,
    )

    ai_policy = models.CharField(
        "سياسة استخدام الذكاء الاصطناعي",
        max_length=30,
        choices=AIPolicy.choices,
        default=AIPolicy.DISCLOSURE_REQUIRED,
    )

    subject = models.ForeignKey(
        "academics.Subject",
        on_delete=models.CASCADE,
        related_name="activities",
        verbose_name="المقرر",
    )

    unit = models.ForeignKey(
        "academics.Unit",
        on_delete=models.SET_NULL,
        related_name="activities",
        null=True,
        blank=True,
        verbose_name="الوحدة",
    )

    lesson = models.ForeignKey(
        "academics.Lesson",
        on_delete=models.SET_NULL,
        related_name="activities",
        null=True,
        blank=True,
        verbose_name="الدرس",
    )

    term = models.ForeignKey(
        "academics.Term",
        on_delete=models.CASCADE,
        related_name="activities",
        verbose_name="الفصل الدراسي",
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="created_activities",
        limit_choices_to={"role": "teacher"},
        verbose_name="المعلمة",
    )

    classrooms = models.ManyToManyField(
        "academics.Classroom",
        through="ActivityAssignment",
        related_name="activities",
        verbose_name="الشعب المستهدفة",
    )

    max_score = models.DecimalField(
        "الدرجة النهائية",
        max_digits=6,
        decimal_places=2,
        default=10,
    )

    opens_at = models.DateTimeField(
        "بداية استقبال الأعمال",
        null=True,
        blank=True,
    )

    due_at = models.DateTimeField(
        "موعد التسليم",
        null=True,
        blank=True,
    )

    allow_late_submission = models.BooleanField(
        "السماح بالتسليم المتأخر",
        default=True,
    )

    allowed_extensions = models.JSONField(
        "امتدادات الملفات المسموحة",
        default=list,
        blank=True,
        help_text="مثال: pdf, jpg, png, mp4",
    )

    max_files = models.PositiveSmallIntegerField(
        "الحد الأعلى لعدد الملفات",
        default=5,
    )

    max_file_size_mb = models.PositiveIntegerField(
        "الحد الأعلى لحجم الملف بالميجابايت",
        default=100,
    )

    reference_file = models.FileField(
        "ملف إرشادي",
        upload_to="activities/references/",
        null=True,
        blank=True,
    )

    is_published = models.BooleanField(
        "منشور للطالبات",
        default=False,
        db_index=True,
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
        verbose_name = "نشاط"
        verbose_name_plural = "الأنشطة"
        ordering = ["-created_at"]

    def __str__(self):
        return self.title


class ActivityAssignment(models.Model):
    """إسناد النشاط إلى شعبة واحدة أو أكثر."""

    activity = models.ForeignKey(
        Activity,
        on_delete=models.CASCADE,
        related_name="classroom_assignments",
        verbose_name="النشاط",
    )

    classroom = models.ForeignKey(
        "academics.Classroom",
        on_delete=models.CASCADE,
        related_name="activity_assignments",
        verbose_name="الشعبة",
    )

    assigned_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="assigned_activities",
        verbose_name="تم الإسناد بواسطة",
    )

    assigned_at = models.DateTimeField(
        "تاريخ الإسناد",
        auto_now_add=True,
    )

    class Meta:
        verbose_name = "إسناد نشاط"
        verbose_name_plural = "إسنادات الأنشطة"
        constraints = [
            models.UniqueConstraint(
                fields=["activity", "classroom"],
                name="unique_activity_classroom",
            )
        ]

    def __str__(self):
        return f"{self.activity} - {self.classroom}"    