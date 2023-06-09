from types import MethodType

from django.apps import apps
from django.conf import settings
from django.core import checks


def check_user_model(app_configs=None, **kwargs):
    if app_configs is None:
        cls = apps.get_model(settings.AUTH_USER_MODEL)
    else:
        app_label, model_name = settings.AUTH_USER_MODEL.split(".")
        for app_config in app_configs:
            if app_config.label == app_label:
                cls = app_config.get_model(model_name)
                break
        else:
            # Checks might be run against a set of app configs that don't
            # include the specified user model. In this case we simply don't
            # perform the checks defined below.
            return []

    errors = []

    # Check that REQUIRED_FIELDS is a list
    if not isinstance(cls.REQUIRED_FIELDS, (list, tuple)):
        errors.append(
            checks.Error(
                "'REQUIRED_FIELDS' must be a list or tuple.",
                obj=cls,
                id="auth.E001",
            )
        )

    # Check that the USERNAME FIELD isn't included in REQUIRED_FIELDS.
    if cls.USERNAME_FIELD in cls.REQUIRED_FIELDS:
        errors.append(
            checks.Error(
                "The field named as the 'USERNAME_FIELD' "
                "for a custom user model must not be included in 'REQUIRED_FIELDS'.",
                hint=(
                    "The 'USERNAME_FIELD' is currently set to '%s', you "
                    "should remove '%s' from the 'REQUIRED_FIELDS'."
                    % (cls.USERNAME_FIELD, cls.USERNAME_FIELD)
                ),
                obj=cls,
                id="auth.E002",
            )
        )

    # Check that the username field is unique
    if not cls._meta.get_field(cls.USERNAME_FIELD).unique and not any(
        constraint.fields == (cls.USERNAME_FIELD,)
        for constraint in cls._meta.total_unique_constraints
    ):
        if settings.AUTHENTICATION_BACKENDS == [
            "django.contrib.auth.backends.ModelBackend"
        ]:
            errors.append(
                checks.Error(
                    "'%s.%s' must be unique because it is named as the "
                    "'USERNAME_FIELD'." % (cls._meta.object_name, cls.USERNAME_FIELD),
                    obj=cls,
                    id="auth.E003",
                )
            )
        else:
            errors.append(
                checks.Warning(
                    "'%s.%s' is named as the 'USERNAME_FIELD', but it is not unique."
                    % (cls._meta.object_name, cls.USERNAME_FIELD),
                    hint=(
                        "Ensure that your authentication backend(s) can handle "
                        "non-unique usernames."
                    ),
                    obj=cls,
                    id="auth.W004",
                )
            )

    if isinstance(cls().is_anonymous, MethodType):
        errors.append(
            checks.Critical(
                "%s.is_anonymous must be an attribute or property rather than "
                "a method. Ignoring this is a security issue as anonymous "
                "users will be treated as authenticated!" % cls,
                obj=cls,
                id="auth.C009",
            )
        )
    if isinstance(cls().is_authenticated, MethodType):
        errors.append(
            checks.Critical(
                "%s.is_authenticated must be an attribute or property rather "
                "than a method. Ignoring this is a security issue as anonymous "
                "users will be treated as authenticated!" % cls,
                obj=cls,
                id="auth.C010",
            )
        )
    return errors
