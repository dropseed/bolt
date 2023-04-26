import logging

from django.http import (
    HttpRequest,
    HttpResponse,
    HttpResponseNotAllowed,
)
from django.utils.decorators import classonlymethod

from .exceptions import HttpResponseException

logger = logging.getLogger("django.request")


class View:
    http_method_names = [
        "get",
        "post",
        "put",
        "patch",
        "delete",
        "head",
        "options",
        "trace",
    ]

    def __init__(self, request: HttpRequest, *args, **kwargs) -> None:
        if hasattr(self, "get") and not hasattr(self, "head"):
            self.head = self.get

        self.request = request
        self.url_args = args
        self.url_kwargs = kwargs

    @property
    def args(self) -> tuple:
        # Warning - old name
        return self.url_args

    @property
    def kwargs(self) -> dict:
        # Warning - old name
        return self.url_kwargs

    @classonlymethod
    def as_view(cls):
        def view(request, *args, **kwargs):
            v = cls(request, *args, **kwargs)
            return v.get_response()

        # Copy possible attributes set by decorators, e.g. @csrf_exempt, from
        # the dispatch method.
        view.__dict__.update(cls.get_response.__dict__)
        view.view_class = cls

        return view

    def get_response(self) -> HttpResponse:
        return self.dispatch()

    def dispatch(self, *args, **kwargs) -> HttpResponse:
        """Compatible with Django's dispatch, but we disregard the args/kwargs"""
        # Warning?

        if not self.request.method:
            raise AttributeError("HTTP method is not set")

        if self.request.method.lower() not in self.http_method_names:
            return self._http_method_not_allowed()

        handler = getattr(
            self, self.request.method.lower(), self._http_method_not_allowed
        )
        try:
            return handler()
        except HttpResponseException as e:
            return e.response

    def _http_method_not_allowed(self) -> HttpResponse:
        logger.warning(
            "Method Not Allowed (%s): %s",
            self.request.method,
            self.request.path,
            extra={"status_code": 405, "request": self.request},
        )
        return HttpResponseNotAllowed(self._allowed_methods())

    def options(self) -> HttpResponse:
        """Handle responding to requests for the OPTIONS HTTP verb."""
        response = HttpResponse()
        response.headers["Allow"] = ", ".join(self._allowed_methods())
        response.headers["Content-Length"] = "0"
        return response

    def _allowed_methods(self) -> list[str]:
        return [m.upper() for m in self.http_method_names if hasattr(self, m)]
