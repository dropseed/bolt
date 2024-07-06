from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "test"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_PACKAGES = [
    "plain.auth",
    "plain.sessions",
    "plain.importmap",
    "app",
]

MIDDLEWARE = [
    "plain.middleware.security.SecurityMiddleware",
    "plain.sessions.middleware.SessionMiddleware",
    "plain.middleware.common.CommonMiddleware",
    "plain.csrf.middleware.CsrfViewMiddleware",
    "plain.auth.middleware.AuthenticationMiddleware",
    "plain.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "app.urls"

WSGI_APPLICATION = "wsgi.application"


# Database

DATABASES = {
    "default": {
        "ENGINE": "plain.models.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}


# Internationalization

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)

ASSETS_URL = "/assets/"
