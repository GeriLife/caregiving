from datetime import timedelta
from django.db import connection
from django.db.models import Sum, Value
from django.db.models.functions import Concat, TruncMonth
from django.utils import timezone
import pandas as pd

from core.constants import HOUR_MINUTES, YEAR_DAYS


def dictfetchall(cursor):
    """Return a list of dictionaries containing all rows from a database
    cursor."""
    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]


def get_daily_total_hours_by_role_and_work_type_with_percent(home_id):
    query = """
    with daily_work_totals_by_type as (
        select
            date,
            caregiver_role.name as role_name,
            work_type.name as work_type,
            sum(duration_minutes) / 60.0 as daily_total_hours
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
            sum(duration_minutes) / 60.0 as total_hours
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
            CAST(sum(duration_minutes) / 60.0 as FLOAT) as total_hours
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


def home_monthly_activity_hours_by_type(home) -> pd.DataFrame:
    """Returns a list of dictionaries of hours of activities grouped by month
    and type."""

    from metrics.models import ResidentActivity

    today = timezone.now()
    one_year_ago = today - timedelta(days=YEAR_DAYS)

    activities = (
        ResidentActivity.objects.filter(
            activity_date__gte=one_year_ago,
            home=home,
        )
        .annotate(
            month=TruncMonth("activity_date"),
        )
        .values("month", "activity_type")
        .order_by("month")
        .annotate(activity_hours=Sum("activity_minutes") / HOUR_MINUTES)
    )

    return pd.DataFrame(list(activities))


def home_monthly_activity_hours_by_caregiver_role(home) -> pd.DataFrame:
    """Returns a DataFrame of hours of activities grouped by month and
    caregiver role."""

    from metrics.models import ResidentActivity

    today = timezone.now()
    one_year_ago = today - timedelta(days=YEAR_DAYS)

    activities = (
        ResidentActivity.objects.filter(
            activity_date__gte=one_year_ago,
            home=home,
        )
        .annotate(
            month=TruncMonth("activity_date"),
        )
        .values("month", "caregiver_role")
        .order_by("month")
        .annotate(activity_hours=Sum("activity_minutes") / HOUR_MINUTES)
    )

    return pd.DataFrame(list(activities))


def home_activity_hours_by_resident_and_type(home) -> pd.DataFrame:
    """Returns a DataFrame of hours of activities grouped by resident and
    activity type."""

    from metrics.models import ResidentActivity

    today = timezone.now()
    one_year_ago = today - timedelta(days=YEAR_DAYS)

    activities = (
        ResidentActivity.objects.filter(
            activity_date__gte=one_year_ago,
            home=home,
        )
        .values("resident", "activity_type")
        .order_by("resident")
        .annotate(
            full_name=Concat(
                "resident__first_name",
                Value(" "),
                "resident__last_initial",
            ),
        )
        .annotate(activity_hours=Sum("activity_minutes") / HOUR_MINUTES)
    )

    return pd.DataFrame(list(activities))
