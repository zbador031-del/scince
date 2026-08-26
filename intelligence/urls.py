from django.urls import path

from . import monthly_views, student_reports, views


app_name = "intelligence"


urlpatterns = [
    # مؤشرات وتحليلات المعلمة
    path(
        "teacher/analytics/",
        views.teacher_analytics,
        name="teacher_analytics",
    ),

    # قائمة التقارير الفردية لجميع الطالبات
    path(
        "teacher/students/reports/",
        student_reports.student_reports_list,
        name="student_reports_list",
    ),

    # التقرير التحليلي الفردي لطالبة من جهة المعلمة
    path(
        "teacher/students/<int:portfolio_id>/report/",
        student_reports.student_analytics_report,
        name="student_analytics_report",
    ),

    # التقرير الشخصي للطالبة المسجلة
    path(
        "student/my-report/",
        student_reports.my_student_analytics_report,
        name="my_student_analytics_report",
    ),

    # أرشيف تقارير عالمة الشهر
    path(
        "teacher/monthly-honors/",
        monthly_views.monthly_honor_archive,
        name="monthly_honor_archive",
    ),

    # التقرير الشهري التفصيلي
    path(
        "teacher/monthly-honors/<int:honor_id>/",
        monthly_views.monthly_honor_report,
        name="monthly_honor_report",
    ),
]