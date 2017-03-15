from __future__ import with_statement
from fabric.api import task, env, run, local, roles, cd, execute, hide, puts, sudo, prefix
import re
import os
import sys
import time
import datetime
import logging
import shutil
import MySQLdb
import random
import yaml
from subprocess import Popen, PIPE
from fabric.operations import prompt
from fabric.contrib.console import confirm
from fabric.context_managers import lcd
from fabric.colors import green
from fabric.contrib import django

os.environ["DJANGO_SETTINGS_MODULE"] = "cali_water_reports.settings_production"

from django.conf import settings

env.project_name = 'cali_water_reports'
env.local_branch = 'master'
env.remote_ref = 'origin/master'
env.requirements_file = 'requirements.txt'
env.use_ssh_config = True

CONFIG_PATH = "%s_CONFIG_PATH" % (env.project_name.upper())
CONFIG_FILE = os.environ.setdefault(CONFIG_PATH, "./development.yml")
CONFIG = yaml.load(open(CONFIG_FILE))

logger = logging.getLogger("root")
logging.basicConfig(
    format = "\033[1;36m%(levelname)s: %(filename)s (def %(funcName)s %(lineno)s): \033[1;37m %(message)s",
    level=logging.DEBUG
)


# data processing and update functions
def test():
    """
    run the cali_water application tests before attempting to update with new data
    """
    local("python manage.py test")


def fetch_enforcement_stats():
    """
    ingest the latest enforcement data from the state water resources board
    """
    local("python manage.py fetch_enforcement_stats")


def fetch_water_use():
    """
    ingest the latest usage data from the state water resources board
    """
    local("python manage.py fetch_usage_stats")


# development functions
def run():
    """
    shortcut for base manage.py function to run the dev server
    """
    local("python manage.py runserver")


def make():
    """
    shortcut for base manage.py function to sync the dev database
    """
    local("python manage.py makemigrations")


def migrate():
    """
    shortcut for base manage.py function to apply db migrations
    """
    local("python manage.py migrate")


def superuser():
    """
    shortcut for base manage.py function to create a superuser
    """
    local("python manage.py createsuperuser")


# data export functions
def dump_regions():
    """
    shortcut to dump hydrologic region data fixtures
    """
    local("python manage.py dumpdata monthly_water_reports.hydrologicregion > monthly_water_reports/fixtures/hydrologic_regions.json")


def dump_suppliers():
    """
    shortcut to dump water supplier data fixtures
    """
    local("python manage.py dumpdata monthly_water_reports.watersupplier > monthly_water_reports/fixtures/water_suppliers.json")


def dump_reports():
    """
    shortcut to dump monthly water supplier use reports data fixtures
    """
    local("python manage.py dumpdata monthly_water_reports.watersuppliermonthlyreport > monthly_water_reports/fixtures/supplier_reports.json")


def dump_enforcement():
    """
    shortcut to dump monthly water supplier enforcement statistics data fixtures
    """
    local("python manage.py dumpdata monthly_water_reports.waterenforcementmonthlyreport > monthly_water_reports/fixtures/enforcement_reports.json")


def dump_conservation():
    """
    shortcut to dump water conservation data fixtures
    """
    local("python manage.py dumpdata monthly_water_reports.waterconservationmethod > monthly_water_reports/fixtures/conservation_methods.json")


def dump_fixtures():
    """
    shortcut to dump all data fixtures with logging
    """
    logger.debug("Dumping out data fixtures for %s django project" % (CONFIG["database"]["database"]))
    dump_regions()
    logger.debug("Regions are exported")
    dump_suppliers()
    logger.debug("Suppliers are exported")
    dump_enforcement()
    logger.debug("Enforcement stats are exported")
    dump_conservation()
    logger.debug("Conservation methods are exported")
    dump_reports()
    logger.debug("Monthly reports are exported")


# data import functions
def load_regions():
    """
    shortcut to load hydrologic region data fixtures
    """
    local("python manage.py loaddata monthly_water_reports/fixtures/hydrologic_regions.json")


def load_suppliers():
    """
    shortcut to load water supplier data fixtures
    """
    local("python manage.py loaddata monthly_water_reports/fixtures/water_suppliers.json")


def load_reports():
    """
    shortcut to load monthly water supplier use reports data fixtures
    """
    local("python manage.py loaddata monthly_water_reports/fixtures/supplier_reports.json")


def load_enforcement():
    """
    shortcut to load monthly water supplier enforcement statistics data fixtures
    """
    local("python manage.py loaddata monthly_water_reports/fixtures/enforcement_reports.json")


def load_conservation():
    """
    shortcut to load water conservation data fixtures
    """
    local("python manage.py loaddata monthly_water_reports/fixtures/conservation_methods.json")


def load_fixtures():
    """
    shortcut to load all data fixtures with logging
    """
    logger.debug("Loading data fixtures for %s django project" % (CONFIG["database"]["database"]))
    load_regions()
    logger.debug("Regions are loaded")
    load_suppliers()
    logger.debug("Suppliers are loaded")
    load_enforcement()
    logger.debug("Enforcement stats are loaded")
    load_conservation()
    logger.debug("Conservation methods are loaded")
    load_reports()
    logger.debug("Monthly reports are loaded")

# bootstrapping functions
def rename_files():
    """
    shortcut to install requirements from repository's requirements.txt
    """
    os.rename("cali_water_reports/settings_common.py.template", "cali_water_reports/settings_common.py")
    os.rename("cali_water_reports/settings_production.py.template", "cali_water_reports/settings_production.py")


def requirements():
    """
    shortcut to install requirements from repository's requirements.txt
    """
    local("pip install -r requirements.txt")


def create_db():
    """
    shortcut to create the database for the monthly water numbers project
    """
    connection = None
    db_config = CONFIG["database"]
    logger.debug("Creating %s database for %s django project" % (db_config["database"], env.project_name))
    create_statement = "CREATE DATABASE %s" % (db_config["database"])
    try:
        connection = MySQLdb.connect(
            host = db_config["host"],
            user = db_config["username"],
            passwd = db_config["password"]
        )
        cursor = connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(create_statement)
        connection.commit()
    except MySQLdb.DatabaseError, e:
        print "Error %s" % (e)
        sys.exit(1)
    finally:
        if connection:
            connection.close()


def makesecret(length=50, allowed_chars='abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)'):
    """
    generates secret key for use in django settings
    https://github.com/datadesk/django-project-template/blob/master/fabfile/makesecret.py
    """
    key = ''.join(random.choice(allowed_chars) for i in range(length))
    print 'secret_key: "%s"' % key


def build():
    """
    build the static html pages for the project
    """
    local("python manage.py build")


def buildserver():
    local("python manage.py buildserver")


def bootstrap():
    """
    run tasks to setup the base project
    """
    create_db()
    time.sleep(2)
    migrate()
    time.sleep(2)
    load_fixtures()
    time.sleep(2)
    local("python manage.py createsuperuser")
    run()


def __env_cmd(cmd):
    return env.bin_root + cmd
