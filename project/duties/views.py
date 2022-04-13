from typing import Any, Dict

from django.db.models import Sum
from django.views.generic import TemplateView

from .models import Duty


class DutiesReportView(TemplateView):
    template_name = "duties/report.html"

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)

        context["duties_daily_sum"] = (
            Duty.objects.values("date")
            .order_by("date")
            .annotate(total_minutes=Sum("duration"))
        )

        context["duties_type_sum"] = (
            Duty.objects.values("type__name")
            .order_by("type__name")
            .annotate(total_minutes=Sum("duration"))
        )

        context["duties_caregiver_role_sum"] = (
            Duty.objects.values("caregiver_role__name")
            .order_by("caregiver_role__name")
            .annotate(total_minutes=Sum("duration"))
        )

        return context

