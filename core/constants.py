from django.utils.translation import gettext_lazy as _

# Activity ranges
#
# Based on the count of activities in the past seven days:
# - inactive: almost no activities
# - low: a few activities
# - good: an appropriate amount of activities
# - high: a lot of activities (maybe too many)
#
# Note: range ends are exclusive, so the max value is the same as the next
# range's min value.
WEEKLY_ACTIVITY_RANGES = {
    "inactive": {  # Includes only 0.
        "color_class": "danger",
        "label": _("Inactive"),
        "min_inclusive": 0,
        "max_inclusive": 0,
        "range": range(0, 1),
    },
    "low": {  # Includes 1, 2, 3, 4.
        "color_class": "warning",
        "label": _("Low"),
        "min_inclusive": 1,
        "max_inclusive": 4,
        "range": range(1, 5),
    },
    "good": {  # Includes 5, 6, 7, 8, 9.
        "color_class": "success",
        "label": _("Moderate"),
        "min_inclusive": 5,
        "max_inclusive": 9,
        "range": range(5, 10),
    },
    "high": {  # Includes 10 onwards ... (1000 is arbitrary).
        "color_class": "warning",
        "label": _("High"),
        "min_inclusive": 10,
        "max_inclusive": 1000,
        "range": range(10, 1001),
    },
}
