from django.urls import path

from . import views


app_name = "assessment"


urlpatterns = [
    # تقييم عمل طالبة واحدة
    path(
        "submissions/<int:submission_id>/evaluate/",
        views.evaluate_submission,
        name="evaluate_submission",
    ),

    # تقييم عدة أعمال دفعة واحدة
    path(
        "submissions/bulk-evaluate/",
        views.bulk_evaluate_submissions,
        name="bulk_evaluate_submissions",
    ),
]