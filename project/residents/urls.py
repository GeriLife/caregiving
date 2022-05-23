from django.urls import path

from .views import (
    ResidentDetailView,
)

urlpatterns = [
    path("<slug:pk>/", ResidentDetailView.as_view(), name="resident-detail"),
]