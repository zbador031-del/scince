from django.urls import path

from . import views


app_name = "academics"


urlpatterns = [
    # صفوف وشعب المعلمة
    path(
        "teacher/classrooms/",
        views.teacher_classrooms,
        name="teacher_classrooms",
    ),

    # تفاصيل الشعبة والطالبات
    path(
        "classrooms/<int:classroom_id>/",
        views.classroom_detail,
        name="classroom_detail",
    ),
]