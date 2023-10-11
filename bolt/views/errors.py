from bolt.http import HttpResponseBase

from .templates import TemplateView


class ErrorView(TemplateView):
    status_code: int

    def __init__(self, status_code=None) -> None:
        # Allow creating an ErrorView with a status code
        # e.g. ErrorView.as_view(status_code=404)
        if status_code is not None:
            self.status_code = status_code

    def get_template_names(self) -> list[str]:
        return [f"{self.status_code}.html", "error.html"]

    def get_response(self) -> HttpResponseBase:
        response = super().get()  # All methods (post, patch, etc.) will use the get()
        response.status_code = self.status_code
        return response