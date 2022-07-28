from typing import Any, Dict

from django.db import connection
from django.db.models import Sum
from django.utils.translation import gettext as _
from django.views.generic import TemplateView
from django.views.generic.edit import FormView

import plotly.express as px

from .forms import WorkForm
from .models import Work

minutes_in_hour = 60.0


def dictfetchall(cursor):
    """Return a list of dictionaries containing all rows from a database cursor"""
    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]


def get_daily_total_hours_by_role_and_work_type_with_percent():
    query = """
    with daily_work_totals_by_type as (
        select
            date,
            caregiver_role.name as role_name,
            work_type.name as work_type, 
            sum(duration) / 60.0 as daily_total_hours
        from work
        left join work_type on type_id = work_type.id
        left join caregiver_role on caregiver_role_id = caregiver_role.id
        group by date, role_name, work_type
    ),
    daily_work_totals_by_type_with_role_total_hours as (
        select 
            *,
            sum(daily_total_hours) over (partition by date, role_name) as daily_role_total_hours
        from daily_work_totals_by_type
    )

    select 
        *,
        CAST(daily_total_hours as float) / CAST(daily_role_total_hours as float) as percent_of_daily_role_total_hours
    from daily_work_totals_by_type_with_role_total_hours;
    """

    with connection.cursor() as cursor:
        cursor.execute(query)

        result = dictfetchall(cursor)

    return result


def get_total_hours_by_role_and_work_type_with_percent():
    query = """
    with work_totals_by_type as (
        select 
            caregiver_role.name as role_name,
            work_type.name as work_type, 
            sum(duration) / 60.0 as total_hours
        from work
        left join work_type on type_id = work_type.id
        left join caregiver_role on caregiver_role_id = caregiver_role.id
        group by role_name, work_type
    ),
    work_totals_by_type_with_role_total_hours as (
        select 
            *,
            sum(total_hours) over (partition by role_name) as role_total_hours
        from work_totals_by_type
    )

    select 
        *,
        CAST(total_hours as float) / CAST(role_total_hours as float) as percent_of_role_total_hours
    from work_totals_by_type_with_role_total_hours;
    """

    with connection.cursor() as cursor:
        cursor.execute(query)

        result = dictfetchall(cursor)

    return result

def get_work_by_type_data():
    work_by_type = (
        Work.objects
            .values("type__name")
            .order_by("type__name")
            .annotate(total_hours=Sum("duration") / minutes_in_hour)
    )

    return list(work_by_type)

def prepare_work_by_type_chart(data):
    work_by_type_chart = px.bar(
        data,
        x="type__name",
        y="total_hours",
        title=_("Work hours by work type"),
        labels={
            "type__name": _("Type of work"),
            "total_hours": _("Total hours"),
        },
    ).to_html()

    return work_by_type_chart


def get_work_by_caregiver_role_data():
    work_by_caregiver_role_data = (
        Work.objects
            .values("caregiver_role__name")
            .order_by("caregiver_role__name")
            .annotate(total_hours=Sum("duration") / 60.0)
    )

    return list(work_by_caregiver_role_data)

def prepare_work_by_caregiver_role_chart(data):
    work_by_caregiver_role_chart = px.bar(
        data,
        x="caregiver_role__name",
        y="total_hours",
        title=_("Work hours by caregiver role"),
        labels={
            "caregiver_role__name": _("Caregiver role"),
            "total_hours": _("Total hours"),
        },
    ).to_html()

    return work_by_caregiver_role_chart


def prepare_daily_work_percent_by_caregiver_role_and_type_chart(data):
    daily_work_percent_by_caregiver_role_and_type_chart = px.bar(
        data,
        x="date",
        y="percent_of_daily_role_total_hours",
        facet_row="role_name",
        color="work_type",
        title=_("Daily work percent by caregiver role and work type"),
        labels={
            "role_name": _("Caregiver role"),
            "percent_of_daily_role_total_hours": _("Work percent"),
            "work_type": _("Type of work"),
        },
        # Add numeric text on bars
        text_auto=True,
    )

    # Format y-axis as percentages
    daily_work_percent_by_caregiver_role_and_type_chart.update_yaxes(tickformat = ",.0%")
    
    # Remove facet prefix from facet row labels
    daily_work_percent_by_caregiver_role_and_type_chart.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
    
    # Ensure that all bar widths are one day (where units are in milliseconds)
    one_day = 24 * 60 * 60 * 1000
    daily_work_percent_by_caregiver_role_and_type_chart.update_traces(width=one_day)

    return daily_work_percent_by_caregiver_role_and_type_chart.to_html()

def prepare_work_percent_by_caregiver_role_and_type_chart(data):
    work_percent_by_caregiver_role_and_type_chart = px.bar(
        data,
        x="role_name",
        y="percent_of_role_total_hours",
        color="work_type",
        title=_("Work percent by caregiver role and work type"),
        labels={
            "role_name": _("Caregiver role"),
            "percent_of_role_total_hours": _("Work percent"),
            "work_type": _("Type of work"),
        },
        text_auto=True,
    )
    work_percent_by_caregiver_role_and_type_chart.layout.yaxis.tickformat = ",.0%"

    return work_percent_by_caregiver_role_and_type_chart.to_html()

def prepare_work_by_caregiver_role_and_type_chart(data):
    work_by_caregiver_role_and_type_chart = px.bar(
        data,
        x="role_name",
        y="total_hours",
        color="work_type",
        title=_("Work hours by caregiver role and work type"),
        labels={
            "role_name": _("Caregiver role"),
            "total_hours": _("Total hours"),
            "work_type": _("Type of work"),
        },
    
    )

    return work_by_caregiver_role_and_type_chart.to_html()


class WorkReportView(TemplateView):
    template_name = "work/report.html"

    def prepare_charts(self, context):
        """Prepare data/charts and add them to the template context"""
        work_by_type_data = get_work_by_type_data()
        context["work_by_type_chart"] = prepare_work_by_type_chart(work_by_type_data)

        work_by_caregiver_role_data = get_work_by_caregiver_role_data()
        context["work_by_caregiver_role_chart"] = prepare_work_by_caregiver_role_chart(work_by_caregiver_role_data)

        daily_total_hours_by_role_and_work_type_with_percent_data = get_daily_total_hours_by_role_and_work_type_with_percent()
        context["daily_work_percent_by_caregiver_role_and_type_chart"] = prepare_daily_work_percent_by_caregiver_role_and_type_chart(
            daily_total_hours_by_role_and_work_type_with_percent_data
        )

        work_by_caregiver_role_and_type_with_percent = get_total_hours_by_role_and_work_type_with_percent()
        context["work_percent_by_caregiver_role_and_type_chart"] = prepare_work_percent_by_caregiver_role_and_type_chart(
            work_by_caregiver_role_and_type_with_percent
        )
        context["work_by_caregiver_role_and_type_chart"] = prepare_work_by_caregiver_role_and_type_chart(
            work_by_caregiver_role_and_type_with_percent
        )

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
