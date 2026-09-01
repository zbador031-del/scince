from datetime import date
from unittest.mock import patch

from django.test import RequestFactory, TestCase

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

        # يجب أن يظهر الاسم مرة واحدة ولو تعددت أعمال الطالبة المتميزة.
        Submission.objects.create(
            portfolio=portfolio,
            title="عمل أول",
            is_featured=True,
        )
        Submission.objects.create(
            portfolio=portfolio,
            title="عمل ثانٍ",
            status=Submission.Status.FEATURED,
        )

    @patch("intelligence.context_processors.cache.get", return_value=True)
    def test_all_featured_students_are_listed_once(self, _cache_get):
        context = monthly_honor_ticker(RequestFactory().get("/"))

        self.assertEqual(
            context["featured_student_names"],
            ["ريم الزهراني"],
        )
