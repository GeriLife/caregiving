from django.urls import path

from .views import HomeListView

urlpatterns = [
    path("", HomeListView.as_view(), name="home-list-view"),
]
