from django.urls import reverse_lazy
from django.views.generic import ListView, FormView
from django.db import transaction
from .forms import ActivityForm
from .models import Activity
from residents.models import Residency
from metrics.models import ResidentActivity


class ActivityFormView(FormView):
    template_name = "activities/form.html"
    form_class = ActivityForm
    # get the url to the activity list view
    success_url = reverse_lazy("activity-list-view")

    @transaction.atomic
    def form_valid(self, form):
        # save the form before redirecting to success URL
        # Note: this may be unnecessary,
        # but the form wasn't saving previously
        def add_resident_activity(data, activity):
            for resident in data["residents"]:
                activity = activity
                try:
                    residency = Residency.objects.get(
                        resident=resident,
                        move_out__isnull=True,
                    )
                except Residency.DoesNotExist:
                    print("Residency doesn't exist")
                    transaction.set_rollback(True)
                    return
                home = residency.home
                activity_type = data["activity_type"]
                activity_minutes = data["duration_minutes"]
                caregiver_role = data["caregiver_role"]

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

        a = form.save()
        add_resident_activity(form.cleaned_data, Activity.objects.get(id=a.id))
        return super().form_valid(form)


class ActivityListView(ListView):
    template_name = "activities/list.html"
    queryset = Activity.objects.all()
    context_object_name = "activities"
    paginate_by = 10
    ordering = ["-date"]
