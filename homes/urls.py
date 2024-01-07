from django.urls import path

from .views import HomeDetailView, HomeGroupListView, HomeUserRelationListView

urlpatterns = [
    path(
        "<str:url_uuid>/",
        HomeDetailView.as_view(),
        name="home-detail-view",
    ),
    path(
        "<str:url_uuid>/caregivers/",
        HomeUserRelationListView.as_view(),
        name="home-user-relation-list-view",
    ),
    path(
        "",
        HomeGroupListView.as_view(),
        name="home-list-view",
    ),
]
