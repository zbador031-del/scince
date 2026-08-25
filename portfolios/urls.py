from django.urls import path

from . import views


app_name = "portfolios"


urlpatterns = [
    # دفتر الطالبة
    path(
        "my-portfolio/",
        views.student_portfolio,
        name="student_portfolio",
    ),

    # رفع عمل جديد
    path(
        "my-portfolio/upload/",
        views.upload_submission,
        name="upload_submission",
    ),

    # قائمة أعمال الطالبات للمعلمة
    path(
        "teacher/submissions/",
        views.teacher_submissions,
        name="teacher_submissions",
    ),

    # تفاصيل عمل طالبة
    path(
        "teacher/submissions/<int:submission_id>/",
        views.teacher_submission_detail,
        name="teacher_submission_detail",
    ),
]