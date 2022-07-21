from django.urls import path

from .views import HomeDetailView, HomeListView

urlpatterns = [
    path('<pk>/', HomeDetailView.as_view(), name='home-detail-view'),
    path("", HomeListView.as_view(), name="home-list-view"),
]
