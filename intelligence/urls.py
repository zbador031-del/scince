from django.urls import path

from . import views


app_name = "intelligence"


urlpatterns = [
    # مؤشرات وتحليلات المعلمة
    path(
        "teacher/analytics/",
        views.teacher_analytics,
        name="teacher_analytics",
    ),
]