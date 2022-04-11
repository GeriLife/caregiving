from typing import Any, Dict
from django.views.generic import TemplateView

class DutiesReportView(TemplateView):
    template_name = 'duties/report.html'

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        return super().get_context_data(**kwargs)
