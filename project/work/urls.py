from django.urls import path
from django.utils.translation import gettext_lazy as _

from .views import WorkFormView, WorkReportView

urlpatterns = [
    path(_("submit/"), WorkFormView.as_view(), name="work-form-view"),
    path(_("report/"), WorkReportView.as_view(), name="work-report-view"),
]
