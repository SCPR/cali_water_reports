from __future__ import division
from django.conf import settings
from django.core.management.base import BaseCommand
import time
import datetime
import logging
from monthly_water_reports.fetch_enforcement_stats import LoadMonthlyEnforcementStats

logger = logging.getLogger("cali_water_reports")

class Command(BaseCommand):
    help = "Begin a request to State Water Resources Board for latest usage report"
    def handle(self, *args, **options):
        task_run = LoadMonthlyEnforcementStats()
        task_run._init()
        self.stdout.write("\nTask finished at %s\n" % str(datetime.datetime.now()))
