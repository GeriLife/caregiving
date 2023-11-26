from django.urls import path
from django.utils.translation import gettext_lazy as _

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
        "<slug:pk>/",
        ResidentDetailView.as_view(),
        name="resident-detail-view",
    ),
    path(
        "",
        ResidentListView.as_view(),
        name="resident-list-view",
    ),
    path(
        "<slug:pk>/update/",
        ResidentUpdateView.as_view(),
        name="resident-update-view",
    ),
]
