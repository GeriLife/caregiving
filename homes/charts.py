from django.db import connection
from django.db.models import Sum
from django.utils.translation import gettext as _

import plotly.express as px


def dictfetchall(cursor):
    """Return a list of dictionaries containing all rows from a database
    cursor."""
    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]


def get_activity_counts_by_resident_and_activity_type(home_id):
    query = """
        SELECT COUNT(ra.resident) AS activity_count, ra.activity_type AS activity_type, CONCAT(r.first_name,' ',r.last_name) AS resident_name
        FROM resident_activity AS ra
        JOIN resident AS r ON ra.resident = r.id
        WHERE ra.home = %s
        GROUP BY ra.resident, ra.activity_type
    """
    with connection.cursor() as cursor:
        cursor.execute(query, [home_id])

        result = dictfetchall(cursor)

    return result


def prepare_activity_counts_by_resident_and_activity_type(home):
    activity_counts_by_resident_and_activity_type = (
        get_activity_counts_by_resident_and_activity_type(home.id)
    )

    activity_counts_by_resident_and_activity_type_chart = px.bar(
        activity_counts_by_resident_and_activity_type,
        x="activity_count",
        y="resident_name",
        color="activity_type",
        orientation="h",
        title=_("Resident Activity Count By Type"),
        labels={
            "activity_count": _("Activity Count"),
            "resident_name": _("Resident Name"),
        },
    ).to_html()

    return activity_counts_by_resident_and_activity_type_chart


def get_daily_total_hours_by_role_and_work_type_with_percent(home_id):
    query = """
    with daily_work_totals_by_type as (
        select
            date,
            caregiver_role.name as role_name,
            work_type.name as work_type,
            sum(duration_hours) as daily_total_hours
        from work
        left join work_type on type_id = work_type.id
        left join caregiver_role on caregiver_role_id = caregiver_role.id
        where home_id = %s
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
        cursor.execute(query, [home_id])

        result = dictfetchall(cursor)

    return result


def get_total_hours_by_role_and_work_type_with_percent(home_id):
    query = """
    with work_totals_by_type as (
        select
            caregiver_role.name as role_name,
            work_type.name as work_type,
            sum(duration_hours) as total_hours
        from work
        left join work_type on type_id = work_type.id
        left join caregiver_role on caregiver_role_id = caregiver_role.id
        where home_id = %s
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
        cursor.execute(query, [home_id])

        result = dictfetchall(cursor)

    return result


def get_home_total_hours_by_role_with_percent(home_id):
    query = """
    with work_totals_by_caregiver_role as (
        select
            home.name as home_name,
            caregiver_role.name as role_name,
            CAST(sum(duration_hours) as FLOAT) as total_hours
        from work
        left join home on home_id = home.id
        left join caregiver_role on caregiver_role_id = caregiver_role.id
        where home_id = %s
        group by home_name, role_name
    )

    select
        *,
        (total_hours / SUM(total_hours) over ()) as percent_of_role_total_hours
    from work_totals_by_caregiver_role;
    """

    with connection.cursor() as cursor:
        cursor.execute(query, [home_id])

        result = dictfetchall(cursor)

    return result


def prepare_work_by_type_chart(home):
    work_by_type = list(
        home.work_performed.values("type__name")
        .order_by("type__name")
        .annotate(total_hours=Sum("duration_hours")),
    )

    work_by_type_chart = px.bar(
        work_by_type,
        x="type__name",
        y="total_hours",
        title=_("Work hours by type"),
        labels={
            "type__name": _("Type of work"),
            "total_hours": _("Total hours"),
        },
    ).to_html()

    return work_by_type_chart


def prepare_work_by_caregiver_role_chart(home):
    work_by_caregiver_role = list(
        home.work_performed.values("caregiver_role__name")
        .order_by("caregiver_role__name")
        .annotate(total_hours=Sum("duration_hours")),
    )

    work_by_caregiver_role_chart = px.bar(
        work_by_caregiver_role,
        x="caregiver_role__name",
        y="total_hours",
        title=_("Work hours by caregiver role"),
        labels={
            "caregiver_role__name": _("Caregiver role"),
            "total_hours": _("Total hours"),
        },
    ).to_html()

    return work_by_caregiver_role_chart


def prepare_daily_work_percent_by_caregiver_role_and_type_chart(home):
    daily_total_hours_by_role_and_work_type_with_percent = (
        get_daily_total_hours_by_role_and_work_type_with_percent(home.id)
    )

    daily_work_percent_by_caregiver_role_and_type_chart = px.bar(
        daily_total_hours_by_role_and_work_type_with_percent,
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
    daily_work_percent_by_caregiver_role_and_type_chart.update_yaxes(tickformat=",.0%")

    # Remove facet prefix from facet row labels
    daily_work_percent_by_caregiver_role_and_type_chart.for_each_annotation(
        lambda a: a.update(text=a.text.split("=")[-1]),
    )

    # Ensure that all bar widths are one day (where units are in milliseconds)
    one_day = 24 * 60 * 60 * 1000
    daily_work_percent_by_caregiver_role_and_type_chart.update_traces(width=one_day)

    return daily_work_percent_by_caregiver_role_and_type_chart.to_html()


def prepare_home_work_percent_by_caregiver_role_chart(home):
    home_work_percent_by_caregiver_role = get_home_total_hours_by_role_with_percent(
        home.id,
    )

    home_work_percent_by_caregiver_role_chart = px.bar(
        home_work_percent_by_caregiver_role,
        color="role_name",
        x="percent_of_role_total_hours",
        y="home_name",
        labels={
            "role_name": _("Caregiver role"),
            "percent_of_role_total_hours": "",
            "home_name": "",
        },
        text_auto=True,
    )

    home_work_percent_by_caregiver_role_chart.update_layout(
        height=100,
        margin={
            "b": 0,
            "l": 0,
            "r": 0,
            "t": 0,
            "pad": 0,
        },
        plot_bgcolor="rgba(0, 0, 0, 0)",
        showlegend=False,
        xaxis={
            "tickformat": ",.0%",
        },
        yaxis={
            "visible": False,
        },
    )

    return home_work_percent_by_caregiver_role_chart.to_html(
        config={
            "displayModeBar": False,
        },
    )


def prepare_work_percent_by_caregiver_role_and_type_chart(
    work_by_caregiver_role_and_type_with_percent,
):
    work_percent_by_caregiver_role_and_type_chart = px.bar(
        work_by_caregiver_role_and_type_with_percent,
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


def prepare_work_by_caregiver_role_and_type_chart(
    work_by_caregiver_role_and_type_with_percent,
):
    work_by_caregiver_role_and_type_chart = px.bar(
        work_by_caregiver_role_and_type_with_percent,
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


def prepare_work_by_caregiver_role_and_type_charts(context):
    home = context["home"]

    work_by_caregiver_role_and_type_with_percent = (
        get_total_hours_by_role_and_work_type_with_percent(home.id)
    )

    context[
        "work_percent_by_caregiver_role_and_type_chart"
    ] = prepare_work_percent_by_caregiver_role_and_type_chart(
        work_by_caregiver_role_and_type_with_percent,
    )

    context[
        "work_by_caregiver_role_and_type_chart"
    ] = prepare_work_by_caregiver_role_and_type_chart(
        work_by_caregiver_role_and_type_with_percent,
    )

    return context
