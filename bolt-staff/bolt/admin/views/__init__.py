from .base import (
    AdminDeleteView,
    AdminDetailView,
    AdminListView,
    AdminUpdateView,
    AdminView,
)
from .models import (
    AdminModelDetailView,
    AdminModelListView,
    AdminModelUpdateView,
    AdminModelViewset,
)
from .registry import (
    register_dashboard,
    register_view,
    register_viewset,
)

__all__ = [
    "AdminView",
    "AdminListView",
    "AdminDetailView",
    "AdminUpdateView",
    "AdminDeleteView",
    "AdminModelViewset",
    "AdminModelListView",
    "AdminModelDetailView",
    "AdminModelUpdateView",
    "register_viewset",
    "register_view",
    "register_dashboard",
]
