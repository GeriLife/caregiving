from django.urls import reverse_lazy
from django.views.generic import ListView, FormView

from .forms import ActivityForm
from .models import Activity


class ActivityFormView(FormView):
    template_name = "activities/form.html"
    form_class = ActivityForm
    # get the url to the activity list view
    success_url = reverse_lazy("activity-list-view")

    def add_resident_activity(self, data):
        for r in data["residents"]:
            print("Placeholder")
            # resident = r
            # activity =
            # try:
            #     residency = Residency.objects.get(resident=r, move_out__isnull=True)
            # except Residency.DoesNotExist:
            #     print("Residency doesn't exist for this resident")
            #     return
            # home = residency.home
            # activity_type = data[activity_type]
            # activity_minutes = data[duration_minutes]
            # caregiver_role = data[caregiver_role]

            # resident_activity = ResidentActivity.objects.create(
            #     resident=resident,
            #     activity=activity,
            #     residency=residency,
            #     home=home,
            #     activity_type=activity_type,
            #     activity_minutes=activity_minutes,
            #     caregiver_role=caregiver_role,
            # )
            # resident_activity.save()

    def form_valid(self, form):
        # save the form before redirecting to success URL
        # Note: this may be unnecessary,
        # but the form wasn't saving previously
        form.save()
        self.add_resident_activity(form.cleaned_data)

        return super().form_valid(form)


class ActivityListView(ListView):
    template_name = "activities/list.html"
    queryset = Activity.objects.all()
    context_object_name = "activities"
    paginate_by = 10
    ordering = ["-date"]
