from . import settings


def can_be_impersonator(user):
    return settings.IMPERSONATE_ALLOWED(user)


def can_impersonate_user(impersonator, target_user):
    if not can_be_impersonator(impersonator):
        return False

    # You can't impersonate staff users
    if target_user.is_staff:
        return False

    return True
