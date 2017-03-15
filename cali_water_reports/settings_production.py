# Django settings for cali_water_reports project.

# -*- coding: utf-8 -*-
import os
from os.path import expanduser
from settings_common import *
import pytz
from pytz import timezone
import yaml

CONFIG_PATH = "%s_CONFIG_PATH" % ("cali_water_reports".upper())
CONFIG_FILE = os.environ.setdefault(CONFIG_PATH, "./development.yml")
CONFIG = yaml.load(open(CONFIG_FILE))

DEBUG = CONFIG.get("debug", False)
TEMPLATE_DEBUG = DEBUG

INTERNAL_IPS = CONFIG.get("internal_ips", None)

DATABASES = {
    "default": {
        "ENGINE" : "django.db.backends.mysql",
        "NAME" : CONFIG["database"]["database"],
        "USER" : CONFIG["database"]["username"],
        "PASSWORD" : CONFIG["database"]["password"],
        "HOST" : CONFIG["database"]["host"],
        "PORT" : CONFIG["database"]["port"]
    }
}

SECRET_KEY = CONFIG["secret_key"]

REQUEST_HEADERS = {
    "From": CONFIG["api"]["headers"]["from"],
    "User-agent": CONFIG["api"]["headers"]["user_agent"]
}

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

if CONFIG["installed_apps"]:
    INSTALLED_APPS += tuple(CONFIG["installed_apps"])

# Python dotted path to the WSGI application used by Django"s runserver.
WSGI_APPLICATION = "cali_water_reports.wsgi.application"

ADMIN_MEDIA_PREFIX = "/media/"

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = ""

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = ""

# Absolute path to the directory static files should be collected to.
# Don"t put anything in this directory yourself; store your static files
# in apps" "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = os.path.join(SITE_ROOT, "public", "static")

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = "/static/"

SITE_URL = "#"

# Additional locations of static files
STATICFILES_DIRS = (

)

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
if "build" in CONFIG:
    BAKERY_GZIP = CONFIG["build"]["bakery_gzip"]
    STAGING = CONFIG["build"]["staging"]
    STAGING_PREFIX = CONFIG["build"]["staging_prefix"]
    LIVE_PREFIX = CONFIG["build"]["live_prefix"]
    DEPLOY_DIR = CONFIG["build"]["deploy_dir"]
    STATIC_DIR = STATIC_URL
    BUILD_DIR = CONFIG["build"]["build_dir"]
    BAKERY_VIEWS = tuple(CONFIG["build"]["views"])
    URL_PATH = ""

# paths and variables for state water data
if "data_source" in CONFIG:
    DATA_PATH = CONFIG["data_source"]["data_path"]
    FILE_DOWNLOAD_PATH = CONFIG["data_source"]["file_download_path"]
    # ENFORCEMENT_FILE = CONFIG["data_source"]["enforcement_file"]
    USAGE_FILE = CONFIG["data_source"]["usage_file"]
