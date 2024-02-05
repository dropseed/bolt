import os
import time
import warnings

from bolt.signals import setting_changed
from bolt.signals.dispatch import Signal, receiver
from bolt.utils import timezone
from bolt.utils.functional import empty

template_rendered = Signal()

# Most setting_changed receivers are supposed to be added below,
# except for cases where the receiver is related to a contrib app.

# Settings that may not work well when using 'override_settings' (#19031)
COMPLEX_OVERRIDE_SETTINGS = {"DATABASES"}


@receiver(setting_changed)
def update_installed_packages(*, setting, **kwargs):
    if setting == "INSTALLED_PACKAGES":
        # Rebuild any PackageDirectoriesFinder instance.
        from bolt.assets.finders import get_finder

        get_finder.cache_clear()
        # Rebuild management commands cache
        from bolt.legacy.management import get_commands

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

    try:
        from bolt.db import connections
    except ImportError:
        return

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
def asset_storage_changed(*, setting, **kwargs):
    if setting in {
        "ASSETS_BACKEND",
        "ASSETS_ROOT",
        "ASSETS_URL",
    }:
        from bolt.assets.storage import assets_storage

        assets_storage._wrapped = empty


@receiver(setting_changed)
def asset_finders_changed(*, setting, **kwargs):
    if setting in {
        "ASSETS_ROOT",
    }:
        from bolt.assets.finders import get_finder

        get_finder.cache_clear()


@receiver(setting_changed)
def auth_password_validators_changed(*, setting, **kwargs):
    if setting == "AUTH_PASSWORD_VALIDATORS":
        from bolt.auth.password_validation import (
            get_default_password_validators,
        )

        get_default_password_validators.cache_clear()
