import json
from typing import Any, Dict

from django.db import connection
from django.db.models import Sum
from django.utils.translation import gettext as _
from django.views.generic import TemplateView
from django.views.generic.edit import FormView

import pandas as pd
import plotly.express as px

from .forms import WorkForm
from .models import Work


def dictfetchall(cursor):
    """Return a list of dictionaries containing all rows from a database cursor"""
    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]


def get_total_minutes_by_role_and_work_type():
    query = """
    select 
        caregiver_role.name as role_name,
        work_type.name as work_type, 
        sum(duration) as total_minutes
    from work
    left join work_type on type_id = work_type.id
    left join caregiver_role on caregiver_role_id = caregiver_role.id
    group by role_name, work_type;
    """

    with connection.cursor() as cursor:
        cursor.execute(query)

        result = dictfetchall(cursor)

    return result


class WorkReportView(TemplateView):
    template_name = "work/report.html"

    def prepare_charts(self, context):
        """Prepare charts and add them to the template context"""
        work_daily_sum = list(
            Work.objects.values("date")
            .order_by("date")
            .annotate(total_minutes=Sum("duration"))
        )
        context["work_daily_sum"] = work_daily_sum

        context["work_daily_sum_max"] = max(
            daily_sum["total_minutes"] for daily_sum in context["work_daily_sum"]
        )

        work_by_type = list(
            Work.objects.values("type__name")
            .order_by("type__name")
            .annotate(total_minutes=Sum("duration"))
        )

        context["work_by_type_chart"] = px.bar(
            work_by_type,
            x="type__name",
            y="total_minutes",
            title=_("Work minutes by type"),
            labels={
                "type__name": _("Type of work"),
                "total_minutes": _("Total minutes"),
            },
        ).to_html()

        work_by_caregiver_role = list(
            Work.objects.values("caregiver_role__name")
            .order_by("caregiver_role__name")
            .annotate(total_minutes=Sum("duration"))
        )

        context["work_by_caregiver_role_chart"] = px.bar(
            work_by_caregiver_role,
            x="caregiver_role__name",
            y="total_minutes",
            title=_("Work minutes by caregiver role"),
            labels={
                "caregiver_role__name": _("Caregiver role"),
                "total_minutes": _("Total minutes"),
            },
        ).to_html()

        work_by_caregiver_role_and_type = get_total_minutes_by_role_and_work_type()

        context["work_by_caregiver_role_and_type_chart"] = px.histogram(
            work_by_caregiver_role_and_type,
            x="role_name",
            y="total_minutes",
            color="work_type",
            title=_("Work minutes by caregiver role and work type"),
            labels={
                "role_name": _("Caregiver role"),
                "total_minutes": _("total minutes"),
                "work_type": _("Type of work"),
            },
        ).to_html()

        return context

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)

        # Check if work has been recorded
        # by selecting one record
        context["work_has_been_recorded"] = Work.objects.all()[:1].exists()

        # Only prepare charts if work has been recorded
        if context["work_has_been_recorded"]:
            context = self.prepare_charts(context)

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
