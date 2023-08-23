import os
import time
import warnings

from bolt.apps import apps
from bolt.exceptions import ImproperlyConfigured
from bolt.signals import setting_changed
from bolt.db import connections, router
from bolt.db.utils import ConnectionRouter
from bolt.signals.dispatch import Signal, receiver
from bolt.utils import timezone
from bolt.utils.functional import empty
from bolt.utils.module_loading import import_string

template_rendered = Signal()

# Most setting_changed receivers are supposed to be added below,
# except for cases where the receiver is related to a contrib app.

# Settings that may not work well when using 'override_settings' (#19031)
COMPLEX_OVERRIDE_SETTINGS = {"DATABASES"}


@receiver(setting_changed)
def clear_cache_handlers(*, setting, **kwargs):
    if setting == "CACHES":
        try:
            from bolt.cache import caches, close_caches
        except ImportError:
            return

        close_caches()
        caches._settings = caches.settings = caches.configure_settings(None)
        caches._connections = local()


@receiver(setting_changed)
def update_installed_apps(*, setting, **kwargs):
    if setting == "INSTALLED_APPS":
        # Rebuild any AppDirectoriesFinder instance.
        from bolt.staticfiles.finders import get_finder

        get_finder.cache_clear()
        # Rebuild management commands cache
        from django.core.management import get_commands

        get_commands.cache_clear()


@receiver(setting_changed)
def update_connections_time_zone(*, setting, **kwargs):
    if setting == "TIME_ZONE":
        # Reset process time zone
        if hasattr(time, "tzset"):
            if kwargs["value"]:
                os.environ["TZ"] = kwargs["value"]
            else:
                os.environ.pop("TZ", None)
            time.tzset()

        # Reset local time zone cache
        timezone.get_default_timezone.cache_clear()

    # Reset the database connections' time zone
    if setting in {"TIME_ZONE", "USE_TZ"}:
        for conn in connections.all(initialized_only=True):
            try:
                del conn.timezone
            except AttributeError:
                pass
            try:
                del conn.timezone_name
            except AttributeError:
                pass
            conn.ensure_timezone()


@receiver(setting_changed)
def clear_routers_cache(*, setting, **kwargs):
    if setting == "DATABASE_ROUTERS":
        router.routers = ConnectionRouter().routers


@receiver(setting_changed)
def storages_changed(*, setting, **kwargs):
    from bolt.staticfiles.storage import staticfiles_storage
    from bolt.files.storage import default_storage, storages

    if setting in (
        "STORAGES",
        "STATIC_ROOT",
        "STATIC_URL",
    ):
        try:
            del storages.backends
        except AttributeError:
            pass
        storages._backends = None
        storages._storages = {}

        default_storage._wrapped = empty
        staticfiles_storage._wrapped = empty


@receiver(setting_changed)
def complex_setting_changed(*, enter, setting, **kwargs):
    if enter and setting in COMPLEX_OVERRIDE_SETTINGS:
        # Considering the current implementation of the signals framework,
        # this stacklevel shows the line containing the override_settings call.
        warnings.warn(
            f"Overriding setting {setting} can lead to unexpected behavior.",
            stacklevel=5,
        )


@receiver(setting_changed)
def root_urlconf_changed(*, setting, **kwargs):
    if setting == "ROOT_URLCONF":
        from bolt.urls import clear_url_caches, set_urlconf

        clear_url_caches()
        set_urlconf(None)


@receiver(setting_changed)
def static_storage_changed(*, setting, **kwargs):
    if setting in {
        "STATIC_ROOT",
        "STATIC_URL",
    }:
        from bolt.staticfiles.storage import staticfiles_storage

        staticfiles_storage._wrapped = empty


@receiver(setting_changed)
def static_finders_changed(*, setting, **kwargs):
    if setting in {
        "STATICFILES_DIRS",
        "STATIC_ROOT",
    }:
        from bolt.staticfiles.finders import get_finder

        get_finder.cache_clear()


@receiver(setting_changed)
def auth_password_validators_changed(*, setting, **kwargs):
    if setting == "AUTH_PASSWORD_VALIDATORS":
        from bolt.auth.password_validation import (
            get_default_password_validators,
        )

        get_default_password_validators.cache_clear()


@receiver(setting_changed)
def user_model_swapped(*, setting, **kwargs):
    if setting == "AUTH_USER_MODEL":
        apps.clear_cache()
        try:
            from bolt.auth import get_user_model

            UserModel = get_user_model()
        except ImproperlyConfigured:
            # Some tests set an invalid AUTH_USER_MODEL.
            pass
        else:
            from bolt.auth import backends

            backends.UserModel = UserModel

            from bolt.auth import forms

            forms.UserModel = UserModel

            from bolt.auth import views

            views.UserModel = UserModel