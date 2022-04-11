from django.urls import path

from .views import DutiesReportView

urlpatterns = [
    path('report/', DutiesReportView.as_view(), name='duties-report-view'),
]