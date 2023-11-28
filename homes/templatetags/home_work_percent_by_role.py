from django import template

from homes.charts import prepare_home_work_percent_by_caregiver_role_chart

register = template.Library()


@register.filter(name="work_percent_by_role_chart")
def work_percent_by_role_chart(home):
    """Returns a chart showing the proportion of work carried out by each role
    for the given home."""
    chart = prepare_home_work_percent_by_caregiver_role_chart(home)

    return chart
