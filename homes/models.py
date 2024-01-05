import datetime
from typing import TYPE_CHECKING
from django.contrib.auth import get_user_model
from django.db.models import Count, Q, QuerySet
from django.utils import timezone
from datetime import timedelta
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
import numpy as np
import pandas as pd
from shortuuid.django_fields import ShortUUIDField


from core.constants import WEEK_DAYS, WEEKLY_ACTIVITY_RANGES

if TYPE_CHECKING:
    from residents.models import Resident


user_model = get_user_model()


def _generate_date_range(days_ago: int) -> list[datetime.date]:
    """Generates a list of dates starting from today and going back a specified
    number of days.

    Args:
    days_ago (int): Number of days to go back from today.

    Returns:
    List[datetime.date]: A list of dates.
    """
    today = datetime.date.today()
    return [today - datetime.timedelta(days=x) for x in range(days_ago)]


def _create_resident_date_combinations(
    current_residents: QuerySet,
    date_range: list[datetime.date],
) -> pd.DataFrame:
    """Creates a DataFrame containing combinations of resident IDs, full names,
    and dates.

    Args:
    current_residents (QuerySet): QuerySet of current residents.
    date_range (List[datetime.date]): List of dates for the range.

    Returns:
    pd.DataFrame: DataFrame with resident ID, full name, and activity date for each combination.
        - resident_id: The resident's ID.
        - resident_full_name: The resident's full name.
        - activity_date: The date of the activity.
    """
    resident_date_combinations = [
        {
            "resident_id": resident.id,
            "resident_full_name": resident.full_name,
            "activity_date": activity_date,
        }
        for resident in current_residents
        for activity_date in date_range
    ]
    return pd.DataFrame(resident_date_combinations)


def _get_resident_activities(
    current_residents: QuerySet,
    date_range: list[datetime.date],
) -> pd.DataFrame:
    """Fetches the count of activities for each resident within the specified
    date range.

    Args:
    current_residents (QuerySet): QuerySet of current residents.
    date_range (List[datetime.date]): List of dates for the range.

    Returns:
    pd.DataFrame: DataFrame with resident activities including count.
        - resident_id: The resident's ID.
        - activity_date: The date of the activity.
        - activity_count: The number of activities for the resident on the date.
    """
    from metrics.models import ResidentActivity

    activities = (
        ResidentActivity.objects.filter(
            resident__in=current_residents,
            activity_date__gte=date_range[-1],
        )
        .values("resident_id", "activity_date")
        .annotate(activity_count=Count("id"))
    )
    return pd.DataFrame(list(activities))


def _merge_and_annotate(
    df_combinations: pd.DataFrame,
    df_activities: pd.DataFrame,
) -> pd.DataFrame:
    """Merges two DataFrames and annotates the result with a boolean indicating
    activity presence.

    Args:
    df_combinations (pd.DataFrame): DataFrame of resident-date combinations.
    df_activities (pd.DataFrame): DataFrame of resident activities.

    Returns:
    pd.DataFrame: Merged DataFrame annotated with activity presence.
        - resident_id: The resident's ID.
        - resident_full_name: The resident's full name.
        - activity_date: The date of the activity.
        - activity_count: The number of activities for the resident on the date.
        - had_activity: Boolean indicating whether the resident had activity on the date.
    """
    result = pd.merge(
        df_combinations,
        df_activities,
        how="left",
        on=["resident_id", "activity_date"],
    )
    result["had_activity"] = result["activity_count"] > 0
    return result


def _pivot_resident_data(result: pd.DataFrame) -> pd.DataFrame:
    """Pivots a DataFrame to have residents as rows, dates as columns, and
    activity presence as values.

    Args:
    result (pd.DataFrame): The DataFrame to pivot.

    Returns:
    pd.DataFrame: Pivoted DataFrame with residents and their activities across dates.
        - resident_id: The resident's ID.
        - resident_full_name: The resident's full name.
        - total_activity_count: The total number of activities for the resident.
        - one column for each date in the date range, with a boolean indicating whether the resident had activity on the date.
    """
    pivot_had_activity = result.pivot_table(
        index=["resident_id", "resident_full_name"],
        columns="activity_date",
        values="had_activity",
        fill_value=False,
    )
    total_activity_count = (
        result.groupby(["resident_id", "resident_full_name"])["activity_count"]
        .sum()
        .reset_index()
    )
    total_activity_count.rename(
        columns={"activity_count": "total_activity_count"},
        inplace=True,
    )
    return pd.merge(
        pivot_had_activity.reset_index(),
        total_activity_count,
        on=["resident_id", "resident_full_name"],
        how="left",
    )


def _structure_resident_data(
    pivot_result: pd.DataFrame,
    current_residents: QuerySet,
    date_range: list[datetime.date],
) -> dict:
    """Structures the resident data into a dictionary format for easy access.

    Args:
    pivot_result (pd.DataFrame): Pivoted DataFrame of residents' activities.
    current_residents (QuerySet): QuerySet of current residents.
    date_range (List[datetime.date]): Date range for the activities.

    Returns:
    dict: Dictionary containing structured data about residents' recent activities.
        - start_date: The start date of the date range.
        - end_date: The end date of the date range.
        - residents: A list of dictionaries containing data about each resident.
            - resident: The resident object.
            - total_activity_count: The total number of activities for the resident.
            - recent_activity_days: A list of dictionaries containing data about each day.
    """
    residents_data = []
    for index, row in pivot_result.iterrows():
        resident_data = {
            "resident": current_residents.get(id=row["resident_id"]),
            "total_activity_count": row["total_activity_count"],
            "recent_activity_days": [
                {"date": date, "was_active": row[date]}
                for date in pivot_result.columns
                if isinstance(date, datetime.date)
            ],
        }
        resident_data["total_active_days"] = sum(
            1 for day in resident_data["recent_activity_days"] if day["was_active"]
        )
        residents_data.append(resident_data)

    return {
        "start_date": date_range[-1],
        "end_date": date_range[0],
        "residents": residents_data,
    }


class HomeUserRelation(models.Model):
    user = models.ForeignKey(
        to=user_model,
        on_delete=models.CASCADE,
        related_name="home_user_relations",
    )
    home = models.ForeignKey(
        to="homes.Home",
        on_delete=models.CASCADE,
        related_name="home_user_relations",
    )

    def __str__(self) -> str:
        return f"{self.user} - {self.home}"

    class Meta:
        db_table = "home_user_relation"
        verbose_name = _("home user relation")
        verbose_name_plural = _("home user relations")
        unique_together = ("user", "home")


class Home(models.Model):
    name = models.CharField(max_length=25)
    # add a foreign key relationship to HomeGroup
    home_group = models.ForeignKey(
        to="homes.HomeGroup",
        on_delete=models.PROTECT,
        related_name="homes",
        null=True,
        blank=True,
    )

    url_uuid = ShortUUIDField(
        _("UUID used in URLs"),
        editable=False,  # type: ignore
    )

    class Meta:
        db_table = "home"
        verbose_name = _("home")
        verbose_name_plural = _("homes")

    def __str__(self) -> str:
        return self.name

    def get_absolute_url(self):
        return reverse("home-detail-view", kwargs={"url_uuid": self.url_uuid})

    @property
    def members(self) -> QuerySet[user_model]:
        """Returns a QuerySet of all members of this home."""
        return user_model.objects.filter(home_user_relations__home=self)

    def has_access(self, user: user_model) -> bool:
        """Returns True if the user has access to this home.

        - Superusers have access to all homes.
        - Members of the home have access to the home.
        """
        return user.is_superuser or user in self.members.all()

    @property
    def current_residents(self) -> models.QuerySet["Resident"]:
        """Returns a QuerySet of all current residents for this home."""
        # avoid circular import
        from residents.models import Resident

        return Resident.objects.filter(
            residency__home=self,
            residency__move_out__isnull=True,
        ).order_by("first_name")

    @property
    def current_residents_with_recent_activity_metadata(self):
        current_residents = self.current_residents.all()

        date_range = _generate_date_range(WEEK_DAYS)
        df_combinations = _create_resident_date_combinations(
            current_residents,
            date_range,
        )
        df_activities = _get_resident_activities(current_residents, date_range)

        result = _merge_and_annotate(df_combinations, df_activities)
        pivot_result = _pivot_resident_data(result)
        structured_data = _structure_resident_data(
            pivot_result,
            current_residents,
            date_range,
        )

        return structured_data

    @property
    def residents_with_recent_activity_counts(self) -> QuerySet["Resident"]:
        """Returns a QuerySet of all current residents for this home, annotated
        with a count of recent activities."""
        # Define date range
        today = timezone.now()
        a_week_ago = today - timedelta(days=7)

        # Get current residents
        current_residents = self.current_residents

        # Annotate each resident with a count of recent activities
        residents_with_activities = current_residents.annotate(
            recent_activity_count=Count(
                "resident_activities",
                filter=Q(
                    resident_activities__activity_date__gte=a_week_ago,
                    resident_activities__activity_date__lte=today,
                ),
            ),
        )

        return residents_with_activities

    @property
    def resident_counts_by_activity_level(self) -> dict[str, int]:
        """Returns a dictionary of counts of residents by activity level."""

        annotated_residents = self.residents_with_recent_activity_counts

        # Initialize counts
        activity_counts = {
            "total_count": annotated_residents.count(),
            "inactive_count": 0,
            "low_active_count": 0,
            "good_active_count": 0,
            "high_active_count": 0,
        }

        # Categorize each resident into an activity level
        # and increment the appropriate count
        for resident in annotated_residents:
            activity_count = resident.recent_activity_count

            if activity_count in WEEKLY_ACTIVITY_RANGES["inactive"]["range"]:
                activity_counts["inactive_count"] += 1
            elif activity_count in WEEKLY_ACTIVITY_RANGES["low"]["range"]:
                activity_counts["low_active_count"] += 1
            elif activity_count in WEEKLY_ACTIVITY_RANGES["good"]["range"]:
                activity_counts["good_active_count"] += 1
            elif activity_count in WEEKLY_ACTIVITY_RANGES["high"]["range"]:
                activity_counts["high_active_count"] += 1

        return activity_counts

    def get_resident_percents_by_activity_level_normalized(self) -> dict[str, float]:
        """Returns the resident counts by activity level annotated with a
        percent.

        The percent values, when rounded to the nearest integer, should
        sum to 100.
        """

        activity_counts = self.resident_counts_by_activity_level

        if activity_counts["total_count"] != 0:
            # Calculate raw percentages
            raw_percents = np.array(
                [
                    (activity_counts["inactive_count"] / activity_counts["total_count"])
                    * 100,
                    (
                        activity_counts["low_active_count"]
                        / activity_counts["total_count"]
                    )
                    * 100,
                    (
                        activity_counts["good_active_count"]
                        / activity_counts["total_count"]
                    )
                    * 100,
                    (
                        activity_counts["high_active_count"]
                        / activity_counts["total_count"]
                    )
                    * 100,
                ],
            )

            # Round the percentages
            rounded_percents = np.round(raw_percents).astype(int)

            # Adjust the rounded percentages to sum up to 100
            while rounded_percents.sum() != 100:
                difference = 100 - rounded_percents.sum()
                indices = np.argsort(
                    raw_percents - rounded_percents,
                )  # Get indices to adjust based on largest fractional parts
                for index in indices:
                    should_increment = (
                        difference > 0 and rounded_percents[index] < raw_percents[index]
                    )
                    should_decrement = (
                        difference < 0 and rounded_percents[index] > raw_percents[index]
                    )

                    if should_increment or should_decrement:
                        rounded_percents[index] += np.sign(difference)
                        if rounded_percents.sum() == 100:
                            break

            # Update the activity_counts dictionary with the adjusted percentages
            keys = [
                "inactive_percent",
                "low_active_percent",
                "good_active_percent",
                "high_active_percent",
            ]
            for key, value in zip(keys, rounded_percents):
                activity_counts[key] = value
        else:
            activity_counts["inactive_percent"] = 0
            activity_counts["low_active_percent"] = 0
            activity_counts["good_active_percent"] = 0
            activity_counts["high_active_percent"] = 0

        return activity_counts

    @property
    def resident_counts_by_activity_level_chart_data(self) -> list[dict]:
        """Returns a list of dictionaries of counts of residents by activity
        level."""

        activity_level_counts = (
            self.get_resident_percents_by_activity_level_normalized()
        )

        if not activity_level_counts["total_count"]:
            return []

        chart_data = [
            {
                "activity_level_label": str(
                    WEEKLY_ACTIVITY_RANGES["inactive"]["label"],
                ),
                "activity_level_class": WEEKLY_ACTIVITY_RANGES["inactive"][
                    "color_class"
                ],
                "value": activity_level_counts["inactive_percent"],
            },
            {
                "activity_level_label": str(WEEKLY_ACTIVITY_RANGES["low"]["label"]),
                "activity_level_class": WEEKLY_ACTIVITY_RANGES["low"]["color_class"],
                "value": activity_level_counts["low_active_percent"],
            },
            {
                "activity_level_label": str(WEEKLY_ACTIVITY_RANGES["good"]["label"]),
                "activity_level_class": WEEKLY_ACTIVITY_RANGES["good"]["color_class"],
                "value": activity_level_counts["good_active_percent"],
            },
            {
                "activity_level_label": str(WEEKLY_ACTIVITY_RANGES["high"]["label"]),
                "activity_level_class": WEEKLY_ACTIVITY_RANGES["high"]["color_class"],
                "value": activity_level_counts["high_active_percent"],
            },
        ]

        return chart_data


class HomeGroup(models.Model):
    name = models.CharField(max_length=25)

    url_uuid = ShortUUIDField(
        _("UUID used in URLs"),
        editable=False,  # type: ignore
    )

    class Meta:
        db_table = "home_group"
        verbose_name = _("home group")
        verbose_name_plural = _("home groups")

    def __str__(self) -> str:
        return self.name

    def get_absolute_url(self):
        return reverse("home-group-detail-view", kwargs={"url_uuid": self.url_uuid})
