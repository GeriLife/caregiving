from django.urls import path
from .views import setPreferences

urlpatterns = [
    path(
        "",
        setPreferences,
        name="preferences-view",
    ),
]
