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


def pivot_minutes_by_role_and_work_type(data):
    """
    Pivot the raw aggregation data to a columnar format needed for the chart.

    Each primary sub-group should be a role name with columns for each work type continaing the number of minutes as a value.
    """
    df = pd.DataFrame(data)
    table = pd.pivot_table(
        df, 
        values="total_minutes",
        index=["role_name"],
        columns=["work_type"],
        fill_value=0,
    )

    return table

def prepare_work_minutes_by_role_and_type_chart_traces(pivot_table):
    """Convert pivot table to list of chart traces based on pivot table keys"""
    table_dict = pivot_table.to_dict()

    chart_traces = []

    for role_name, work_performed in table_dict.items():
        work_type_keys = work_performed.keys()
        trace = {
            "name": role_name,
            "x": [work_type for work_type in work_type_keys],
            "y": [work_performed[work_type] for work_type in work_type_keys],
            "type": "bar",
        }

        chart_traces.append(trace)

    return chart_traces


def prepare_minutes_by_role_and_work_type_aggregate():
    data = get_total_minutes_by_role_and_work_type()
    pivot_table = pivot_minutes_by_role_and_work_type(data)
    traces_list = prepare_work_minutes_by_role_and_type_chart_traces(pivot_table)

    return traces_list


class WorkReportView(TemplateView):
    template_name = "work/report.html"

    def prepare_analytics(self, context):
        """Prepare analytics aggregations and add them to the template context"""
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

        context[
            "total_minutes_by_role_and_work_type"
        ] = prepare_minutes_by_role_and_work_type_aggregate()

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
