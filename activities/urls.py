from django.urls import path

# TODO: replace ActivityListView with ResidentActivityListView
from .views import ActivityListView, ResidentActivityFormView


urlpatterns = [
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
