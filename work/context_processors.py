from work.forms import WorkForm


def get_work_form(request):
    """Return an instance of the WorkForm."""
    return {"work_form": WorkForm}
