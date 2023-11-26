from django.db import models
from django.utils.translation import gettext as _
import pandas as pd
import plotly.express as px

from activities.models import Activity


def prepare_daily_activity_minutes_scatter_chart(
    activities: models.QuerySet[Activity],
) -> str:
    """Prepare a scatter chart of daily activity minutes for a resident."""
    activities_agg = (
        activities.values("date")
        .annotate(total_duration_minutes=models.Sum("duration_minutes"))
        .order_by("date")
    )

    df_activities = pd.DataFrame(activities_agg)

    # Ensure 'date' column is in datetime format
    df_activities["date"] = pd.to_datetime(df_activities["date"])

    fig = px.scatter(
        df_activities,
        x="date",
        y="total_duration_minutes",
        title=_("Daily activity minutes"),
        labels={"date": _("Date"), "total_duration_minutes": _("Duration in minutes")},
        trendline="ols",
        trendline_color_override="burlywood",
        hover_data=["total_duration_minutes"],
    )

    fig.update_layout(
        title={
            "y": 0.9,
            "x": 0.5,
            "xanchor": "center",
            "yanchor": "top",
        },
        xaxis_title=_("Date"),
        yaxis_title=_("Duration in minutes"),
        legend_title="",
        template="plotly_dark",
    )

    return fig.to_html()


def prepare_activity_minutes_by_type_chart(
    activities: models.QuerySet[Activity],
) -> str:
    """Prepare a bar chart of activity counts by type for a resident."""
    # This must be a float so that the division below returns a float
    minutes_in_hour = 60.0

    activities_agg = (
        activities.values("activity_type")
        .annotate(total_hours=models.Sum("duration_minutes") / minutes_in_hour)
        .order_by("activity_type")
    )

    df_activities = pd.DataFrame(activities_agg)

    fig = px.bar(
        df_activities,
        x="activity_type",
        y="total_hours",
        title=_("Activity minutes by type"),
        labels={
            "activity_type": _("Type of activity"),
            "total_hours": _("Duration in hours"),
        },
    )

    fig.update_layout(
        title={
            "y": 0.9,
            "x": 0.5,
            "xanchor": "center",
            "yanchor": "top",
        },
        xaxis_title=_("Type of activity"),
        yaxis_title=_("Duration in hours"),
        legend_title="",
        template="plotly_dark",
    )

    return fig.to_html()


def prepare_activity_hours_by_facilitator_role_chart(
    activities: models.QuerySet[Activity],
) -> str:
    """Prepare a bar chart of activity counts by type for a resident."""
    # This must be a float so that the division below returns a float
    minutes_in_hour = 60.0

    activities_agg = (
        activities.values("facilitator_role__title")
        .annotate(total_hours=models.Sum("duration_minutes") / minutes_in_hour)
        .order_by("facilitator_role")
    )

    df_activities = pd.DataFrame(activities_agg)

    fig = px.bar(
        df_activities,
        x="facilitator_role",
        y="total_hours",
        title=_("Activity minutes by facilitator role"),
        labels={
            "facilitator_role": _("Facilitator role"),
            "total_hours": _("Duration in hours"),
        },
    )

    fig.update_layout(
        title={
            "y": 0.9,
            "x": 0.5,
            "xanchor": "center",
            "yanchor": "top",
        },
        xaxis_title=_("Facilitator role"),
        yaxis_title=_("Duration in hours"),
        legend_title="",
        template="plotly_dark",
    )

    return fig.to_html()
