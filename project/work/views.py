from typing import Any, Dict

from django.db.models import Sum
from django.views.generic import TemplateView
from django.views.generic.edit import FormView

from .forms import WorkForm
from .models import Work


class WorkReportView(TemplateView):
    template_name = "work/report.html"

    def prepare_analytics(self, context):
        """Prepare analytics aggregations and add them to the template context"""
        context["work_daily_sum"] = list(
            Work.objects.values("date")
            .order_by("date")
            .annotate(total_minutes=Sum("duration"))
        )
        context["work_daily_sum_max"] = max(
            daily_sum["total_minutes"] for daily_sum in context["work_daily_sum"]
        )

        context["work_type_sum"] = list(
            Work.objects.values("type__name")
            .order_by("type__name")
            .annotate(total_minutes=Sum("duration"))
        )

        context["work_caregiver_role_sum"] = list(
            Work.objects.values("caregiver_role__name")
            .order_by("caregiver_role__name")
            .annotate(total_minutes=Sum("duration"))
        )

        return context

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)

        # Check if work has been recorded
        # by selecting one record
        context["work_has_been_recorded"] = Work.objects.all()[:1].exists()
        
        # Only prepare analytics if work has been recorded
        if context["work_has_been_recorded"]:
            context = self.prepare_analytics(context)

        return context


class WorkFormView(FormView):
    template_name = "work/form.html"
    form_class = WorkForm
    success_url = "/"

    def form_valid(self, form):
        # save the form before redirecting to success URL
        # Note: this may be unnecessary, 
        # but the form wasn't saving previously
        form.save()
        
        return super().form_valid(form)
