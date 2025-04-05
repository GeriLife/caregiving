from django.db.models import Sum, ExpressionWrapper, FloatField
from django.utils.translation import gettext as _

import pandas as pd
import plotly.express as px
from core.constants import DAY_MILLISECONDS, HOUR_MINUTES
from homes.models import Home

from homes.queries import (
    home_activity_hours_by_resident_and_type,
    get_daily_total_hours_by_role_and_work_type_with_percent,
    get_home_total_hours_by_role_with_percent,
    get_total_hours_by_role_and_work_type_with_percent,
    home_monthly_activity_hours_by_caregiver_role,
    home_monthly_activity_hours_by_type,
)

from metrics.models import ResidentActivity


def _apply_activity_type_locale(df: pd.DataFrame) -> pd.DataFrame:
    """Apply the localized labels to the activity_type column."""
    activity_type_mapping = {
        choice.value: _(choice.label) for choice in ResidentActivity.ActivityTypeChoices
    }

    # Apply the mapping to localize the activity_type values
    df["activity_type"] = df["activity_type"].map(activity_type_mapping)


def _apply_caregiver_role_locale(df: pd.DataFrame) -> pd.DataFrame:
    """Apply the localized labels to the caregiver_role column."""
    caregiver_role_mapping = {
        choice.value: _(choice.label)
        for choice in ResidentActivity.CaregiverRoleChoices
    }

    # Apply the mapping to localize the caregiver_role values
    df["caregiver_role"] = df["caregiver_role"].map(caregiver_role_mapping)


def prepare_activity_counts_by_resident_and_activity_type_chart(home: Home) -> str:
    """Prepare the activity counts by resident and activity type chart."""
    activity_counts_by_resident_and_activity_type = (
        home_activity_hours_by_resident_and_type(home)
    )

    _apply_activity_type_locale(activity_counts_by_resident_and_activity_type)

    activity_counts_by_resident_and_activity_type_chart = px.bar(
        activity_counts_by_resident_and_activity_type,
        x="activity_hours",
        y="full_name",
        color="activity_type",
        orientation="h",
        title=_("Resident activity count by type"),
        labels={
            "activity_hours": _("Activity hours"),
            "full_name": _("Resident Name"),
            "activity_type": _("Activity Type"),
        },
        template="plotly_dark",
    )

    # Set plot background/paper color to transparent
    activity_counts_by_resident_and_activity_type_chart.update_layout(
        plot_bgcolor="rgba(0, 0, 0, 0)",
        paper_bgcolor="rgba(0, 0, 0, 0)",
    )

    return activity_counts_by_resident_and_activity_type_chart.to_html()


def prepare_work_by_type_chart(home: Home) -> str:
    """Prepare the work hours by type chart."""
    work_by_type = list(
        home.work_performed.values("type__name")
        .order_by("type__name")
        .annotate(
            total_hours=ExpressionWrapper(
                Sum("duration_minutes") / HOUR_MINUTES,
                output_field=FloatField(),
            ),
        ),
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
        template="plotly_dark",
    )

    # Set plot background/paper color to transparent
    work_by_type_chart.update_layout(
        plot_bgcolor="rgba(0, 0, 0, 0)",
        paper_bgcolor="rgba(0, 0, 0, 0)",
        font_color="#FFFFFF",
    )

    return work_by_type_chart.to_html()


def prepare_work_by_caregiver_role_chart(home: Home) -> str:
    """Prepare the work hours by caregiver role chart."""
    work_by_caregiver_role = list(
        home.work_performed.values("caregiver_role__name")
        .order_by("caregiver_role__name")
        .annotate(
            total_hours=ExpressionWrapper(
                Sum("duration_minutes") / HOUR_MINUTES,
                output_field=FloatField(),
            ),
        ),
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
        template="plotly_dark",
    )

    # Set plot background/paper color to transparent
    work_by_caregiver_role_chart.update_layout(
        plot_bgcolor="rgba(0, 0, 0, 0)",
        paper_bgcolor="rgba(0, 0, 0, 0)",
        font_color="#FFFFFF",
    )

    return work_by_caregiver_role_chart.to_html()


def prepare_daily_work_percent_by_caregiver_role_and_type_chart(home: Home) -> str:
    """Prepare the daily work percent by caregiver role and work type chart."""
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
        template="plotly_dark",
    )

    # Format y-axis as percentages
    daily_work_percent_by_caregiver_role_and_type_chart.update_yaxes(tickformat=",.0%")

    # Remove facet prefix from facet row labels
    daily_work_percent_by_caregiver_role_and_type_chart.for_each_annotation(
        lambda a: a.update(text=a.text.split("=")[-1]),
    )

    # Ensure that all bar widths are one day (where units are in milliseconds)
    daily_work_percent_by_caregiver_role_and_type_chart.update_traces(
        width=DAY_MILLISECONDS,
    )

    # Set plot background/paper color to transparent
    daily_work_percent_by_caregiver_role_and_type_chart.update_layout(
        plot_bgcolor="rgba(0, 0, 0, 0)",
        paper_bgcolor="rgba(0, 0, 0, 0)",
        font_color="#FFFFFF",
    )

    return daily_work_percent_by_caregiver_role_and_type_chart.to_html()


def prepare_home_work_percent_by_caregiver_role_chart(home: Home) -> str:
    """Prepare the home work percent by caregiver role chart."""
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
        template="plotly_dark",
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
        paper_bgcolor="rgba(0, 0, 0, 0)",
        showlegend=False,
        font_color="#FFFFFF",
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
    work_by_caregiver_role_and_type_with_percent: list[dict],
) -> str:
    """Prepare the work percent by caregiver role and work type chart."""
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
        template="plotly_dark",
    )
    work_percent_by_caregiver_role_and_type_chart.layout.yaxis.tickformat = ",.0%"

    # Set plot background/paper color to transparent
    work_percent_by_caregiver_role_and_type_chart.update_layout(
        plot_bgcolor="rgba(0, 0, 0, 0)",
        paper_bgcolor="rgba(0, 0, 0, 0)",
        font_color="#FFFFFF",
    )

    return work_percent_by_caregiver_role_and_type_chart.to_html()


def prepare_work_by_caregiver_role_and_type_chart(
    work_by_caregiver_role_and_type_with_percent: list[dict],
) -> str:
    """Prepare the work hours by caregiver role and work type chart."""
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
        template="plotly_dark",
    )

    # Set plot background/paper color to transparent
    work_by_caregiver_role_and_type_chart.update_layout(
        plot_bgcolor="rgba(0, 0, 0, 0)",
        paper_bgcolor="rgba(0, 0, 0, 0)",
        font_color="#FFFFFF",
    )

    return work_by_caregiver_role_and_type_chart.to_html()


def prepare_work_by_caregiver_role_and_type_charts(context: dict) -> dict:
    home = context["home"]

    work_by_caregiver_role_and_type_with_percent = (
        get_total_hours_by_role_and_work_type_with_percent(home.id)
    )

    context["work_percent_by_caregiver_role_and_type_chart"] = (
        prepare_work_percent_by_caregiver_role_and_type_chart(
            work_by_caregiver_role_and_type_with_percent,
        )
    )

    context["work_by_caregiver_role_and_type_chart"] = (
        prepare_work_by_caregiver_role_and_type_chart(
            work_by_caregiver_role_and_type_with_percent,
        )
    )

    return context


def prepare_monthly_activity_hours_by_type_chart(home: Home) -> str:
    """Prepare the monthly activity hours by type chart."""
    monthly_activity_hours_by_type = home_monthly_activity_hours_by_type(home)

    _apply_activity_type_locale(monthly_activity_hours_by_type)

    monthly_activity_hours_by_type_chart = px.bar(
        monthly_activity_hours_by_type,
        x="month",
        y="activity_hours",
        color="activity_type",
        title=_("Monthly activity hours by type"),
        labels={
            "month": _("Month"),
            "activity_hours": _("Activity hours"),
            "activity_type": _("Activity type"),
        },
    )

    # Set plot background/paper color to transparent
    monthly_activity_hours_by_type_chart.update_layout(
        plot_bgcolor="rgba(0, 0, 0, 0)",
        paper_bgcolor="rgba(0, 0, 0, 0)",
        # ensure text is visible on dark background
        font_color="#FFFFFF",
        # only display month on x-axis
        xaxis={
            "dtick": "M1",
            "tickformat": "%b\n%Y",
        },
    )

    return monthly_activity_hours_by_type_chart.to_html()


def prepare_monthly_activity_hours_by_caregiver_role_chart(home: Home) -> str:
    """Prepare the monthly activity hours by caregiver role chart."""
    monthly_activity_hours_by_caregiver_role = (
        home_monthly_activity_hours_by_caregiver_role(home)
    )

    _apply_caregiver_role_locale(monthly_activity_hours_by_caregiver_role)

    monthly_activity_hours_by_caregiver_role_chart = px.bar(
        monthly_activity_hours_by_caregiver_role,
        x="month",
        y="activity_hours",
        color="caregiver_role",
        title=_("Monthly activity hours by caregiver role"),
        labels={
            "month": _("Month"),
            "caregiver_role": _("Caregiver role"),
            "activity_hours": _("Activity hours"),
        },
    )

    # Set plot background/paper color to transparent
    monthly_activity_hours_by_caregiver_role_chart.update_layout(
        plot_bgcolor="rgba(0, 0, 0, 0)",
        paper_bgcolor="rgba(0, 0, 0, 0)",
        # ensure text is visible on dark background
        font_color="#FFFFFF",
        # only display month on x-axis
        xaxis={
            "dtick": "M1",
            "tickformat": "%b\n%Y",
        },
    )

    return monthly_activity_hours_by_caregiver_role_chart.to_html()
