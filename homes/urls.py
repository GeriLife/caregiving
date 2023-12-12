from django.urls import path

from .views import HomeDetailView, HomeListView, HomeGroupListView

urlpatterns = [
    path("<str:url_uuid>/", HomeDetailView.as_view(), name="home-detail-view"),
    path("", HomeGroupListView.as_view(), name="home-list-view"),
]
