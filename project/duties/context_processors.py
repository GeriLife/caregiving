from django import template


from duties.forms import DutyForm


def get_add_duty_form(request):
    """Return an instance of the DutyForm"""
    return {"add_duty_form": DutyForm}