from django.views.generic.list import ListView

from .models import Home

class HomeListView(ListView):
    model = Home
    context_object_name = "homes"
