from django.urls import reverse_lazy
from django.views.generic import ListView, FormView
from django.db import transaction
from .forms import ActivityForm
from .models import Activity
from residents.models import Residency
from metrics.models import ResidentActivity


def add_resident_activity(activity: Activity):
    for resident in activity.residents.all():
        activity = activity
        try:
            residency = Residency.objects.get(
                resident=resident,
                move_out__isnull=True,
            )
        except Residency.DoesNotExist:
            print("Residency doesn't exist")

            raise

        home = residency.home
        activity_type = activity.activity_type
        activity_minutes = activity.duration_minutes
        caregiver_role = activity.caregiver_role

        resident_activity = ResidentActivity.objects.create(
            resident=resident,
            activity=activity,
            residency=residency,
            home=home,
            activity_type=activity_type,
            activity_minutes=activity_minutes,
            caregiver_role=caregiver_role,
        )
        resident_activity.save()


class ActivityFormView(FormView):
    template_name = "activities/form.html"
    form_class = ActivityForm
    # get the url to the activity list view
    success_url = reverse_lazy("activity-list-view")

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        """Override the post method to add the resident activity in the same
        transaction as the activity."""
        form = self.get_form()
        is_form_valid = form.is_valid()

        if is_form_valid:
            activity = form.save()
            try:
                add_resident_activity(activity)
            except Residency.DoesNotExist:
                transaction.set_rollback(True)
                is_form_valid = False

        return self.form_valid(form) if is_form_valid else self.form_invalid(form)


class ActivityListView(ListView):
    template_name = "activities/list.html"
    queryset = Activity.objects.all()
    context_object_name = "activities"
    paginate_by = 10
    ordering = ["-date"]
