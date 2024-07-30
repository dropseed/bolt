from plain.urls import path
from plain.views import View


class IndexView(View):
    def get(self):
        # Store something so the session is saved
        self.request.session["foo"] = "bar"
        return "test"


urlpatterns = [
    path("", IndexView),
]
