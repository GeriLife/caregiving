from django.db import models
from django.utils.translation import gettext as _
import pandas as pd
import plotly.express as px

from metrics.models import ResidentActivity


def prepare_daily_activity_minutes_scatter_chart(
    activities: models.QuerySet[ResidentActivity],
) -> str:
    """Prepare a scatter chart of daily activity minutes for a resident."""
    activities_agg = (
        activities.values("activity_date")
        .annotate(total_activity_minutes=models.Sum("activity_minutes"))
        .order_by("activity_date")
    )

    df_activities = pd.DataFrame(activities_agg)

    # Ensure 'date' column is in datetime format
    df_activities["activity_date"] = pd.to_datetime(df_activities["activity_date"])

    fig = px.scatter(
        df_activities,
        x="activity_date",
        y="total_activity_minutes",
        title=_("Daily activity minutes"),
        labels={
            "date": _("Date"),
            "total_activity_minutes": _("Total activity minutes"),
        },
        trendline="ols",
        trendline_color_override="burlywood",
        hover_data=["total_activity_minutes"],
    )

    fig.update_layout(
        title={
            "y": 0.9,
            "x": 0.5,
            "xanchor": "center",
            "yanchor": "top",
        },
        xaxis_title=_("Date"),
        yaxis_title=_("Total activity minutes"),
        legend_title="",
        template="plotly_dark",
    )

    return fig.to_html()


def prepare_activity_hours_by_type_chart(
    activities: models.QuerySet[ResidentActivity],
) -> str:
    """Prepare a bar chart of activity counts by type for a resident."""
    # This must be a float so that the division below returns a float
    minutes_in_hour = 60.0

    activities_agg = (
        activities.values("activity_type")
        .annotate(total_hours=models.Sum("activity_minutes") / minutes_in_hour)
        .order_by("activity_type")
    )

    # Retrieve the label for each activity_type
    activities_agg = [
        {
            "activity_type": activity["activity_type"],
            "activity_type_label": str(
                ResidentActivity.ActivityTypeChoices(activity["activity_type"]).label,
            ),
            "total_hours": activity["total_hours"],
        }
        for activity in activities_agg
    ]

    df_activities = pd.DataFrame(activities_agg)

    fig = px.bar(
        df_activities,
        x="activity_type_label",  # Use activity_type_label instead of activity_type
        y="total_hours",
        title=_("Activity hours by type"),
        labels={
            "activity_type_label": _("Type of activity"),  # Update the label for x-axis
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


def prepare_activity_hours_by_caregiver_role_chart(
    activities: models.QuerySet[ResidentActivity],
) -> str:
    """Prepare a bar chart of activity counts by type for a resident."""
    # This must be a float so that the division below returns a float
    minutes_in_hour = 60.0

    activities_agg = (
        activities.values("caregiver_role")
        .annotate(total_hours=models.Sum("activity_minutes") / minutes_in_hour)
        .order_by("caregiver_role")
    )

    # Retrieve the label for each caregiver_role
    activities_agg = [
        {
            "caregiver_role": activity["caregiver_role"],
            "caregiver_role_label": str(
                ResidentActivity.CaregiverRoleChoices(activity["caregiver_role"]).label,
            ),
            "total_hours": activity["total_hours"],
        }
        for activity in activities_agg
    ]

    df_activities = pd.DataFrame(activities_agg)

    fig = px.bar(
        df_activities,
        x="caregiver_role_label",
        y="total_hours",
        title=_("Activity hours by caregiver role"),
        labels={
            "caregiver_role_label": _("Caregiver role"),
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
        xaxis_title=_("Caregiver role"),
        yaxis_title=_("Duration in hours"),
        legend_title="",
        template="plotly_dark",
    )

    return fig.to_html()
