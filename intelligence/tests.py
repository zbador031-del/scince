from datetime import date, timedelta
from unittest.mock import patch

from django.test import RequestFactory, TestCase
from django.utils import timezone

from academics.models import (
    AcademicYear,
    Classroom,
    GradeLevel,
    School,
    Subject,
)
from accounts.models import User
from portfolios.models import Portfolio, Submission

from .context_processors import monthly_honor_ticker


class FeaturedStudentTickerTests(TestCase):
    def setUp(self):
        school = School.objects.create(name="المدرسة")
        academic_year = AcademicYear.objects.create(
            name="1448هـ",
            start_date=date(2026, 8, 1),
            end_date=date(2027, 6, 30),
            is_current=True,
        )
        grade = GradeLevel.objects.create(
            name="الصف الخامس",
            code="5",
        )
        classroom = Classroom.objects.create(
            school=school,
            academic_year=academic_year,
            grade_level=grade,
            name="أ",
        )
        subject = Subject.objects.create(
            name="العلوم",
            code="SCI",
        )
        student = User.objects.create_user(
            username="student1",
            email="student1@example.com",
            first_name="ريم",
            last_name="الزهراني",
            role=User.Role.STUDENT,
        )
        portfolio = Portfolio.objects.create(
            student=student,
            classroom=classroom,
            subject=subject,
            academic_year=academic_year,
        )

        self.first_featured = Submission.objects.create(
            portfolio=portfolio,
            title="عمل أول",
            is_featured=True,
        )
        self.second_featured = Submission.objects.create(
            portfolio=portfolio,
            title="عمل ثانٍ",
            status=Submission.Status.FEATURED,
        )

        collaborator = User.objects.create_user(
            username="student2",
            email="student2@example.com",
            first_name="سارة",
            last_name="الشهري",
            role=User.Role.STUDENT,
        )
        self.first_featured.collaborators.add(collaborator)

        old_featured = Submission.objects.create(
            portfolio=portfolio,
            title="عمل قديم",
            is_featured=True,
        )
        Submission.objects.filter(pk=old_featured.pk).update(
            updated_at=timezone.now() - timedelta(days=8)
        )

    @patch("intelligence.context_processors.cache.get", return_value=True)
    def test_each_featured_student_and_collaborator_is_listed_once(
        self,
        _cache_get,
    ):
        context = monthly_honor_ticker(RequestFactory().get("/"))

        self.assertCountEqual(
            context["featured_student_names"],
            [
                "ريم الزهراني",
                "سارة الشهري",
            ],
        )

    @patch(
        "intelligence.context_processors._get_featured_student_names",
        side_effect=RuntimeError("بيانات شريط غير صالحة"),
    )
    @patch(
        "intelligence.context_processors._get_monthly_honor",
        side_effect=RuntimeError("بيانات تكريم غير صالحة"),
    )
    def test_ticker_failure_never_breaks_site_pages(
        self,
        _monthly_honor,
        _featured_names,
    ):
        context = monthly_honor_ticker(RequestFactory().get("/"))

        self.assertIsNone(context["monthly_honor_ticker"])
        self.assertEqual(context["featured_student_names"], [])
