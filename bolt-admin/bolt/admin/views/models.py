from typing import TYPE_CHECKING

from bolt.db.models import Q
from bolt.urls import reverse_lazy

from .base import URL_NAMESPACE, AdminDetailView, AdminListView, AdminUpdateView

if TYPE_CHECKING:
    from bolt.db import models
    from bolt.views import View


def get_model_field(instance, field):
    if "__" in field:
        # Allow __ syntax like querysets use,
        # also automatically calling callables (like __date)
        result = instance
        for part in field.split("__"):
            result = getattr(result, part)

            # If we hit a None, just return it
            if not result:
                return result

            if callable(result):
                result = result()

        return result

    # Automatically call get_FOO_display() if it exists
    if display := getattr(instance, f"get_{field}_display", None):
        return display()

    return getattr(instance, field)


class AdminModelListView(AdminListView):
    show_search = True

    model: "models.Model"

    fields: list = ["pk"]
    queryset_order = []
    search_fields: list = ["pk"]

    @classmethod
    def get_title(cls) -> str:
        return cls.model._meta.verbose_name_plural.capitalize()

    @classmethod
    def get_slug(cls) -> str:
        return cls.model._meta.model_name

    def get_context(self):
        context = super().get_context()

        order_by = self.request.GET.get("order_by", "")
        if order_by.startswith("-"):
            order_by_field = order_by[1:]
            order_by_direction = "-"
        else:
            order_by_field = order_by
            order_by_direction = ""

        context["order_by_field"] = order_by_field
        context["order_by_direction"] = order_by_direction

        return context

    def get_objects(self):
        queryset = self.get_initial_queryset()
        queryset = self.order_queryset(queryset)
        queryset = self.search_queryset(queryset)
        return queryset

    def get_initial_queryset(self):
        # Separate override for the initial queryset
        # so that annotations can be added BEFORE order_by, etc.
        return self.model.objects.all()

    def order_queryset(self, queryset):
        if order_by := self.request.GET.get("order_by"):
            queryset = queryset.order_by(order_by)
        elif self.queryset_order:
            queryset = queryset.order_by(*self.queryset_order)

        return queryset

    def search_queryset(self, queryset):
        if search := self.request.GET.get("search"):
            filters = Q()
            for field in self.search_fields:
                filters |= Q(**{f"{field}__icontains": search})

            queryset = queryset.filter(filters)

        return queryset

    def get_object_field(self, object, field: str):
        return get_model_field(object, field)


class AdminModelDetailView(AdminDetailView):
    model: "models.Model"
    fields: list = []

    @classmethod
    def get_title(cls) -> str:
        return cls.model._meta.verbose_name.capitalize()

    @classmethod
    def get_slug(cls) -> str:
        return f"{cls.model._meta.model_name}_detail"

    @classmethod
    def get_path(cls) -> str:
        return f"{cls.model._meta.model_name}/<int:pk>/"

    def get_context(self):
        context = super().get_context()
        context["fields"] = self.fields or ["pk"] + [
            f.name for f in self.object._meta.get_fields() if not f.remote_field
        ]
        return context

    def get_object_field(self, object, field: str):
        return get_model_field(object, field)

    def get_object(self):
        return self.model.objects.get(pk=self.url_kwargs["pk"])

    def get_template_names(self) -> list[str]:
        return super().get_template_names() + [
            "admin/detail.html",
        ]


class AdminModelUpdateView(AdminUpdateView):
    model: "models.Model"
    form_class = None  # TODO type annotation
    success_url = "."  # Redirect back to the same update page by default

    @classmethod
    def get_title(cls) -> str:
        return f"Update {cls.model._meta.verbose_name}"

    @classmethod
    def get_slug(cls) -> str:
        return f"{cls.model._meta.model_name}_update"

    @classmethod
    def get_path(cls) -> str:
        return f"{cls.model._meta.model_name}/<int:pk>/update/"

    def get_object(self):
        return self.model.objects.get(pk=self.url_kwargs["pk"])


class AdminModelViewset:
    @classmethod
    def get_views(cls) -> list["View"]:
        views = []

        if hasattr(cls, "ListView") and hasattr(cls, "DetailView"):
            cls.ListView.get_detail_url = lambda self, obj: reverse_lazy(
                f"{URL_NAMESPACE}:{cls.DetailView.view_name()}",
                kwargs={"pk": obj.pk},
            )

            cls.DetailView.parent_view_class = cls.ListView

        if hasattr(cls, "ListView") and hasattr(cls, "UpdateView"):
            cls.ListView.get_update_url = lambda self, obj: reverse_lazy(
                f"{URL_NAMESPACE}:{cls.UpdateView.view_name()}",
                kwargs={"pk": obj.pk},
            )

            cls.UpdateView.parent_view_class = cls.ListView

        if hasattr(cls, "ListView"):
            views.append(cls.ListView)

        if hasattr(cls, "DetailView"):
            views.append(cls.DetailView)

        if hasattr(cls, "UpdateView"):
            views.append(cls.UpdateView)

        return views
