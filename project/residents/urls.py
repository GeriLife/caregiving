from django.urls import path

from .views import (
    ResidentDetailView,
    ResidentListView,
)

urlpatterns = [
    path("<slug:pk>/", ResidentDetailView.as_view(), name="resident-detail"),
    path("", ResidentListView.as_view(), name="resident-list-view",),
]