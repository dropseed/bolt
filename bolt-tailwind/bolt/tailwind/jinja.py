from bolt.jinja.extensions import InclusionTagExtension
from .core import Tailwind
from bolt.runtime import settings


class TailwindCSSExtension(InclusionTagExtension):
    tags = {"tailwind_css"}
    template_name = "tailwind/css.html"

    def get_context(self, context, *args, **kwargs):
        tailwind_static_path = str(settings.TAILWIND_DIST_PATH.relative_to(settings.STATIC_ROOT))
        return {"tailwind_static_path": tailwind_static_path}


extensions = [TailwindCSSExtension]
