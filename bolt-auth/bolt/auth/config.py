from bolt.db.models.query_utils import DeferredAttribute
from bolt.packages import PackageConfig

from . import get_user_model
from .signals import user_logged_in


class AuthConfig(PackageConfig):
    name = "bolt.auth"

    def ready(self):
        last_login_field = getattr(get_user_model(), "last_login", None)
        # Register the handler only if UserModel.last_login is a field.
        if isinstance(last_login_field, DeferredAttribute):
            from .models import update_last_login

            user_logged_in.connect(update_last_login, dispatch_uid="update_last_login")
