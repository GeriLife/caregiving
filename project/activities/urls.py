from django.urls import path
from django.utils.translation import gettext_lazy as _

from .views import ActivityFormView, ActivityListView


urlpatterns = [
    
    path(
        # . Translators: Make sure to leave the trailing slash "/"
        "submit/",
        ActivityFormView.as_view(),
        name="activity-form-view",
    ),
    path(
        # . Translators: Make sure to leave the trailing slash "/"
        "list/",
        ActivityListView.as_view(),
        name="activity-list-view",
    ),
]
