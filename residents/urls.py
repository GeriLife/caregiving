from django.urls import path

from .views import (
    ResidentCreateView,
    ResidentDetailView,
    ResidentListView,
    ResidentUpdateView,
)

urlpatterns = [
    path(
        "create/",
        ResidentCreateView.as_view(),
        name="resident-create-view",
    ),
    path(
        "<str:url_uuid>/",
        ResidentDetailView.as_view(),
        name="resident-detail-view",
    ),
    path(
        "",
        ResidentListView.as_view(),
        name="resident-list-view",
    ),
    path(
        "<str:url_uuid>/update/",
        ResidentUpdateView.as_view(),
        name="resident-update-view",
    ),
]
