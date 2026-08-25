from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """المستخدم الأساسي لجميع حسابات النظام."""

    class Role(models.TextChoices):
        ADMIN = "admin", "مديرة النظام"
        TEACHER = "teacher", "معلمة"
        STUDENT = "student", "طالبة"
        PARENT = "parent", "ولي أمر"

    email = models.EmailField(
        "البريد الإلكتروني",
        unique=True,
        null=True,
        blank=True,
    )

    role = models.CharField(
        "نوع الحساب",
        max_length=20,
        choices=Role.choices,
        default=Role.STUDENT,
        db_index=True,
    )

    phone = models.CharField(
        "رقم الجوال",
        max_length=20,
        unique=True,
        null=True,
        blank=True,
    )

    avatar = models.ImageField(
        "الصورة الشخصية",
        upload_to="profiles/avatars/",
        null=True,
        blank=True,
    )

    is_verified = models.BooleanField(
        "الحساب موثّق",
        default=False,
    )

    created_at = models.DateTimeField(
        "تاريخ إنشاء الحساب",
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        "آخر تحديث",
        auto_now=True,
    )

    # لا يُطلب البريد عند إنشاء الحساب.
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = "مستخدم"
        verbose_name_plural = "المستخدمون"
        ordering = [
            "first_name",
            "last_name",
            "username",
        ]

    def __str__(self):
        full_name = self.get_full_name().strip()
        return full_name or self.username


class TeacherProfile(models.Model):
    """البيانات الإضافية الخاصة بالمعلمة."""

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="teacher_profile",
        limit_choices_to={"role": User.Role.TEACHER},
        verbose_name="المعلمة",
    )

    employee_number = models.CharField(
        "الرقم الوظيفي",
        max_length=30,
        unique=True,
        null=True,
        blank=True,
    )

    specialization = models.CharField(
        "التخصص",
        max_length=100,
        default="العلوم",
        blank=True,
    )

    qualification = models.CharField(
        "المؤهل العلمي",
        max_length=150,
        blank=True,
    )

    bio = models.TextField(
        "نبذة تعريفية",
        blank=True,
    )

    class Meta:
        verbose_name = "ملف معلمة"
        verbose_name_plural = "ملفات المعلمات"

    def __str__(self):
        return f"المعلمة: {self.user}"


class StudentProfile(models.Model):
    """البيانات الإضافية الخاصة بالطالبة."""

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="student_profile",
        limit_choices_to={"role": User.Role.STUDENT},
        verbose_name="الطالبة",
    )

    student_number = models.CharField(
        "الرقم المدرسي",
        max_length=30,
        unique=True,
        null=True,
        blank=True,
    )

    date_of_birth = models.DateField(
        "تاريخ الميلاد",
        null=True,
        blank=True,
    )

    guardian_name = models.CharField(
        "اسم ولي الأمر",
        max_length=150,
        blank=True,
    )

    guardian_phone = models.CharField(
        "رقم جوال ولي الأمر",
        max_length=20,
        blank=True,
    )

    guardian_email = models.EmailField(
        "البريد الإلكتروني لولي الأمر",
        blank=True,
    )

    learning_preferences = models.JSONField(
        "تفضيلات التعلم",
        default=dict,
        blank=True,
    )

    class Meta:
        verbose_name = "ملف طالبة"
        verbose_name_plural = "ملفات الطالبات"

    def __str__(self):
        return f"الطالبة: {self.user}"