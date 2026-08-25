from django.urls import path

from . import views


app_name = "activities"


urlpatterns = [
    # قائمة أنشطة المعلمة
    path(
        "teacher/",
        views.teacher_activity_list,
        name="teacher_activity_list",
    ),

    # إنشاء نشاط جديد
    path(
        "teacher/create/",
        views.teacher_activity_create,
        name="teacher_activity_create",
    ),

    # تعديل نشاط
    path(
        "teacher/<int:activity_id>/edit/",
        views.teacher_activity_update,
        name="teacher_activity_update",
    ),

    # الأنشطة المطلوبة من الطالبة
    path(
        "student/",
        views.student_activity_list,
        name="student_activity_list",
    ),

    # تفاصيل نشاط للطالبة
    path(
        "student/<int:activity_id>/",
        views.student_activity_detail,
        name="student_activity_detail",
    ),
]