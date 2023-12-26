from django.urls import path

from .views import ResidentActivityFormView, ResidentActivityListView


urlpatterns = [
    path(
        "submit/",
        ResidentActivityFormView.as_view(),
        name="resident-activity-form-view",
    ),
    path(
        "list/",
        ResidentActivityListView.as_view(),
        name="activity-list-view",
    ),
]
