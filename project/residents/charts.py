from django.db import models
from django.utils.translation import gettext as _
import pandas as pd
import plotly.express as px


def prepare_daily_activity_minutes_scatter_chart(activities: models.QuerySet) -> str:
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
