from django.urls import path
from django.utils.translation import gettext_lazy as _

from .views import WorkFormView, WorkReportView

urlpatterns = [
    path("submit/", WorkFormView.as_view(), name="work-form-view"),
    path("report/", WorkReportView.as_view(), name="work-report-view"),
]
