from django.conf import settings
from django.db import models


class School(models.Model):
    """بيانات المدرسة وهويتها."""

    name = models.CharField(
        "اسم المدرسة",
        max_length=200,
    )

    education_department = models.CharField(
        "إدارة التعليم",
        max_length=200,
        default="الإدارة العامة للتعليم بعسير",
        blank=True,
    )

    principal_name = models.CharField(
        "اسم مديرة المدرسة",
        max_length=150,
        blank=True,
    )

    logo = models.ImageField(
        "شعار المدرسة",
        upload_to="schools/logos/",
        null=True,
        blank=True,
    )

    address = models.CharField(
        "العنوان",
        max_length=255,
        blank=True,
    )

    phone = models.CharField(
        "رقم التواصل",
        max_length=20,
        blank=True,
    )

    email = models.EmailField(
        "البريد الإلكتروني",
        blank=True,
    )

    is_active = models.BooleanField(
        "مدرسة نشطة",
        default=True,
    )

    class Meta:
        verbose_name = "مدرسة"
        verbose_name_plural = "المدارس"

    def __str__(self):
        return self.name


class AcademicYear(models.Model):
    """العام الدراسي."""

    name = models.CharField(
        "اسم العام الدراسي",
        max_length=30,
        unique=True,
        help_text="مثال: 1448هـ",
    )

    start_date = models.DateField(
        "تاريخ البداية",
    )

    end_date = models.DateField(
        "تاريخ النهاية",
    )

    is_current = models.BooleanField(
        "العام الحالي",
        default=False,
    )

    class Meta:
        verbose_name = "عام دراسي"
        verbose_name_plural = "الأعوام الدراسية"
        ordering = ["-start_date"]

    def __str__(self):
        return self.name


class Term(models.Model):
    """الفصل الدراسي."""

    class TermNumber(models.IntegerChoices):
        FIRST = 1, "الفصل الدراسي الأول"
        SECOND = 2, "الفصل الدراسي الثاني"
        THIRD = 3, "الفصل الدراسي الثالث"

    academic_year = models.ForeignKey(
        AcademicYear,
        on_delete=models.CASCADE,
        related_name="terms",
        verbose_name="العام الدراسي",
    )

    number = models.PositiveSmallIntegerField(
        "الفصل الدراسي",
        choices=TermNumber.choices,
    )

    start_date = models.DateField(
        "تاريخ البداية",
    )

    end_date = models.DateField(
        "تاريخ النهاية",
    )

    is_current = models.BooleanField(
        "الفصل الحالي",
        default=False,
    )

    class Meta:
        verbose_name = "فصل دراسي"
        verbose_name_plural = "الفصول الدراسية"
        ordering = ["academic_year", "number"]
        constraints = [
            models.UniqueConstraint(
                fields=["academic_year", "number"],
                name="unique_term_per_academic_year",
            )
        ]

    def __str__(self):
        return f"{self.get_number_display()} - {self.academic_year}"


class GradeLevel(models.Model):
    """الصف الدراسي مثل الرابع والخامس والسادس."""

    name = models.CharField(
        "اسم الصف",
        max_length=50,
        unique=True,
    )

    code = models.CharField(
        "رمز الصف",
        max_length=20,
        unique=True,
    )

    order = models.PositiveSmallIntegerField(
        "الترتيب",
        default=1,
    )

    class Meta:
        verbose_name = "صف دراسي"
        verbose_name_plural = "الصفوف الدراسية"
        ordering = ["order"]

    def __str__(self):
        return self.name


class Classroom(models.Model):
    """الشعبة الصفية مثل خامس/أ."""

    school = models.ForeignKey(
        School,
        on_delete=models.CASCADE,
        related_name="classrooms",
        verbose_name="المدرسة",
    )

    academic_year = models.ForeignKey(
        AcademicYear,
        on_delete=models.CASCADE,
        related_name="classrooms",
        verbose_name="العام الدراسي",
    )

    grade_level = models.ForeignKey(
        GradeLevel,
        on_delete=models.PROTECT,
        related_name="classrooms",
        verbose_name="الصف",
    )

    name = models.CharField(
        "اسم الشعبة",
        max_length=30,
        help_text="مثال: أ",
    )

    homeroom_teacher = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="homeroom_classrooms",
        null=True,
        blank=True,
        limit_choices_to={"role": "teacher"},
        verbose_name="رائدة الفصل",
    )

    is_active = models.BooleanField(
        "شعبة نشطة",
        default=True,
    )

    class Meta:
        verbose_name = "شعبة صفية"
        verbose_name_plural = "الشعب الصفية"
        ordering = ["grade_level__order", "name"]
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "school",
                    "academic_year",
                    "grade_level",
                    "name",
                ],
                name="unique_classroom_per_year",
            )
        ]

    def __str__(self):
        return f"{self.grade_level} / {self.name}"


class Subject(models.Model):
    """المقرر الدراسي."""

    name = models.CharField(
        "اسم المقرر",
        max_length=100,
        default="العلوم",
    )

    code = models.CharField(
        "رمز المقرر",
        max_length=30,
        unique=True,
    )

    description = models.TextField(
        "وصف المقرر",
        blank=True,
    )

    is_active = models.BooleanField(
        "مقرر نشط",
        default=True,
    )

    class Meta:
        verbose_name = "مقرر"
        verbose_name_plural = "المقررات"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Unit(models.Model):
    """الوحدة التعليمية في المقرر."""

    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        related_name="units",
        verbose_name="المقرر",
    )

    grade_level = models.ForeignKey(
        GradeLevel,
        on_delete=models.CASCADE,
        related_name="units",
        verbose_name="الصف",
    )

    term = models.ForeignKey(
        Term,
        on_delete=models.CASCADE,
        related_name="units",
        verbose_name="الفصل الدراسي",
    )

    title = models.CharField(
        "عنوان الوحدة",
        max_length=200,
    )

    description = models.TextField(
        "وصف الوحدة",
        blank=True,
    )

    order = models.PositiveSmallIntegerField(
        "ترتيب الوحدة",
        default=1,
    )

    class Meta:
        verbose_name = "وحدة تعليمية"
        verbose_name_plural = "الوحدات التعليمية"
        ordering = ["term", "order"]
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "subject",
                    "grade_level",
                    "term",
                    "order",
                ],
                name="unique_unit_order",
            )
        ]

    def __str__(self):
        return self.title


class Lesson(models.Model):
    """درس داخل الوحدة التعليمية."""

    unit = models.ForeignKey(
        Unit,
        on_delete=models.CASCADE,
        related_name="lessons",
        verbose_name="الوحدة",
    )

    title = models.CharField(
        "عنوان الدرس",
        max_length=200,
    )

    learning_objectives = models.TextField(
        "نواتج التعلم",
        blank=True,
    )

    order = models.PositiveSmallIntegerField(
        "ترتيب الدرس",
        default=1,
    )

    is_active = models.BooleanField(
        "درس نشط",
        default=True,
    )

    class Meta:
        verbose_name = "درس"
        verbose_name_plural = "الدروس"
        ordering = ["unit", "order"]
        constraints = [
            models.UniqueConstraint(
                fields=["unit", "order"],
                name="unique_lesson_order_per_unit",
            )
        ]

    def __str__(self):
        return self.title


class Enrollment(models.Model):
    """تسجيل الطالبة في شعبة دراسية."""

    class Status(models.TextChoices):
        ACTIVE = "active", "مستمرة"
        TRANSFERRED = "transferred", "منقولة"
        WITHDRAWN = "withdrawn", "منسحبة"
        COMPLETED = "completed", "مكتملة"

    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="enrollments",
        limit_choices_to={"role": "student"},
        verbose_name="الطالبة",
    )

    classroom = models.ForeignKey(
        Classroom,
        on_delete=models.CASCADE,
        related_name="enrollments",
        verbose_name="الشعبة",
    )

    status = models.CharField(
        "حالة التسجيل",
        max_length=20,
        choices=Status.choices,
        default=Status.ACTIVE,
    )

    joined_at = models.DateField(
        "تاريخ الانضمام",
        auto_now_add=True,
    )

    left_at = models.DateField(
        "تاريخ المغادرة",
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = "تسجيل طالبة"
        verbose_name_plural = "تسجيلات الطالبات"
        ordering = ["classroom", "student__first_name"]
        constraints = [
            models.UniqueConstraint(
                fields=["student", "classroom"],
                name="unique_student_enrollment",
            )
        ]

    def __str__(self):
        return f"{self.student} - {self.classroom}"


class TeachingAssignment(models.Model):
    """إسناد المقرر والمعلمة إلى الشعبة."""

    teacher = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="teaching_assignments",
        limit_choices_to={"role": "teacher"},
        verbose_name="المعلمة",
    )

    classroom = models.ForeignKey(
        Classroom,
        on_delete=models.CASCADE,
        related_name="teaching_assignments",
        verbose_name="الشعبة",
    )

    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        related_name="teaching_assignments",
        verbose_name="المقرر",
    )

    is_active = models.BooleanField(
        "إسناد نشط",
        default=True,
    )

    class Meta:
        verbose_name = "إسناد تدريس"
        verbose_name_plural = "إسنادات التدريس"
        constraints = [
            models.UniqueConstraint(
                fields=["teacher", "classroom", "subject"],
                name="unique_teaching_assignment",
            )
        ]

    def __str__(self):
        return f"{self.teacher} - {self.subject} - {self.classroom}"