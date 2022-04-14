from django.urls import path

from .views import DutyFormView, DutiesReportView

urlpatterns = [
    path("submit/", DutyFormView.as_view(), name="duty-form-view"),
    path("report/", DutiesReportView.as_view(), name="duties-report-view"),
]
