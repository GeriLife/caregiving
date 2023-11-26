from django.urls import reverse_lazy
from django.views.generic import ListView, FormView

from .forms import ActivityForm
from .models import Activity


class ActivityFormView(FormView):
    template_name = "activities/form.html"
    form_class = ActivityForm
    # get the url to the activity list view
    success_url = reverse_lazy("activity-list-view")

    def form_valid(self, form):
        # save the form before redirecting to success URL
        # Note: this may be unnecessary,
        # but the form wasn't saving previously
        form.save()

        return super().form_valid(form)


class ActivityListView(ListView):
    template_name = "activities/list.html"
    queryset = Activity.objects.all()
    context_object_name = "activities"
    paginate_by = 10
    ordering = ["-date"]
