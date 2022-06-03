from django.urls import path

from .views import (
    ResidentDetailView,
    ResidentCreateView,
    ResidentListView,
)

urlpatterns = [
    path("create", ResidentCreateView.as_view(), name="resident-create-view",),
    path("<slug:pk>/", ResidentDetailView.as_view(), name="resident-detail"),
    path("", ResidentListView.as_view(), name="resident-list-view",),
]
