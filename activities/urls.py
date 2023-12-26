from django.urls import path

from .views import ActivityFormView, ActivityListView, ResidentActivityFormView


urlpatterns = [
    path(
        "submit/",
        ActivityFormView.as_view(),
        name="activity-form-view",
    ),
    path(
        "resident-activity/",
        ResidentActivityFormView.as_view(),
        name="resident-activity-form-view",
    ),
    path(
        "list/",
        ActivityListView.as_view(),
        name="activity-list-view",
    ),
]
