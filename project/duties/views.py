from typing import Any, Dict

from django.db.models import Sum
from django.views.generic import TemplateView
from django.views.generic.edit import FormView

from .forms import DutyForm
from .models import Duty


class DutiesReportView(TemplateView):
    template_name = "duties/report.html"

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)

        context["duties_daily_sum"] = list(
            Duty.objects.values("date")
            .order_by("date")
            .annotate(total_minutes=Sum("duration"))
        )
        context["duties_daily_sum_max"] = max(
            daily_sum["total_minutes"] for daily_sum in context["duties_daily_sum"]
        )

        context["duties_type_sum"] = list(
            Duty.objects.values("type__name")
            .order_by("type__name")
            .annotate(total_minutes=Sum("duration"))
        )

        context["duties_caregiver_role_sum"] = list(
            Duty.objects.values("caregiver_role__name")
            .order_by("caregiver_role__name")
            .annotate(total_minutes=Sum("duration"))
        )

        return context


class DutyFormView(FormView):
    template_name = "duties/duty_form.html"
    form_class = DutyForm
    success_url = "/"

    def form_valid(self, form):
        # save the form before redirecting to success URL
        # Note: this may be unnecessary, 
        # but the form wasn't saving previously
        form.save()
        
        return super().form_valid(form)
