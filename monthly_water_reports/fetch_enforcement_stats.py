from __future__ import division
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q, Avg, Max, Min, Sum, Count
from monthly_water_reports.models import WaterSupplier, WaterSupplierMonthlyReport, WaterEnforcementMonthlyReport
from monthly_water_reports.views import QueryUtilities
from fetch_methods import MonthlyFormattingMethods
import csv
from csvkit.utilities.in2csv import In2CSV
import re
import logging
import time
import datetime
import requests
from collections import OrderedDict
import sys
import os.path
import shutil

logger = logging.getLogger("cali_water_reports")

class LoadMonthlyEnforcementStats(object):
    """
    scaffolding to ingest monthly data
    """

    data_path = settings.DATA_PATH

    excel_file_url = settings.USAGE_FILE

    file_name = os.path.basename(excel_file_url)

    file_download_excel_path = "%s/%s" % (settings.FILE_DOWNLOAD_PATH, file_name)

    file_created_csv_path = file_download_excel_path.replace(".xlsx", ".csv")

    list_of_expected_keys = [
        "Supplier Name",
        "Reporting Month",
        "Hydrologic Region",
        "Population Served",
        "Mandatory Restrictions",
        "Water Days Allowed/Week",
        "Complaints Received",
        "Follow-up Actions",
        "Warnings Issued",
        "Penalties Assessed",
        "Enforcement Comments",
    ]

    sluggy = MonthlyFormattingMethods()

    def _init(self, *args, **kwargs):
        """
        begin the process of downloading the latest state water control board usage report
        """
        self.sluggy._can_write_excel_file_from(self.file_name, self.excel_file_url, self.file_download_excel_path)
        self.sluggy._can_convert_excel_file_to(self.file_name, self.file_created_csv_path, self.file_download_excel_path)
        self._can_build_model_instance(self.file_created_csv_path)
        try:
            shutil.move(self.file_download_excel_path, self.data_path)
            shutil.move(self.file_created_csv_path, self.data_path)
        except:
            logger.debug("file already exists in data folder")
            logger.debug("moving %s" % (self.file_name))
            if os.path.exists("%s/%s" % (self.data_path, self.file_name)):
                os.remove("%s/%s" % (self.data_path, self.file_name))
                shutil.move(self.file_download_excel_path, self.data_path)
            logger.debug("moving %s" % (os.path.basename(self.file_created_csv_path)))
            if os.path.exists("%s/%s" % (self.data_path, os.path.basename(self.file_created_csv_path))):
                os.remove("%s/%s" % (self.data_path, os.path.basename(self.file_created_csv_path)))
                shutil.move(self.file_created_csv_path, self.data_path)


    def _can_build_model_instance(self, file_created_csv_path):
        """
        builds data for database from csv file
        """
        with open(file_created_csv_path, "rb") as csvfile:
            csv_data = csv.DictReader(csvfile, delimiter=',')
            for row in csv_data:
                clean_row = {re.sub(r"\([^)]*\)", "", k).strip().replace("- ", "").replace(" ", "_").replace("/", "_").lower(): v.strip() for k, v in row.iteritems()}
                supplier_formatted = self.sluggy._can_prettify_and_slugify_string(clean_row["supplier_name"])
                clean_row["report_date"] = self.sluggy._can_create_datetime_from_filename(file_created_csv_path)
                clean_row["supplier_name"] = supplier_formatted["supplier_name"]
                clean_row["supplier_slug"] = supplier_formatted["supplier_slug"]
                try:
                    clean_row["reporting_month"] = self.sluggy._can_make_string_to_datetime(clean_row["reporting_month"])
                    obj, created = WaterEnforcementMonthlyReport.objects.update_or_create(
                        supplier_slug = clean_row["supplier_slug"],
                        # report_date = clean_row["report_date"],
                        reporting_month = clean_row["reporting_month"],
                        defaults = {
                            "reported_to_state_date": clean_row["reporting_month"],
                            "supplier_name": clean_row["supplier_name"],
                            "hydrologic_region": clean_row["hydrologic_region"],
                            "hydrologic_region_slug": self.sluggy._can_create_hydrologic_region_slug(clean_row["hydrologic_region"]),
                            "enforcement_comments": clean_row["enforcement_comments"],
                            "mandatory_restrictions": clean_row["mandatory_restrictions"],
                            "total_population_served": self.sluggy._can_convert_str_to_num(clean_row["total_population_served"])["value"],
                            "supplier_id": None,
                            "water_days_allowed_week": self.sluggy._can_convert_str_to_num(clean_row["water_days_allowed_week"])["value"],
                            "complaints_received": self.sluggy._can_convert_str_to_num(clean_row["complaints_received"])["value"],
                            "follow_up_actions": self.sluggy._can_convert_str_to_num(clean_row["follow-up_actions"])["value"],
                            "warnings_issued": self.sluggy._can_convert_str_to_num(clean_row["warnings_issued"])["value"],
                            "penalties_assessed": self.sluggy._can_convert_str_to_num(clean_row["penalties_assessed"])["value"],
                        }
                    )
                    if created:
                        logger.debug("%s - %s created" % (clean_row["reporting_month"], clean_row["supplier_name"]))
                    else:
                        logger.debug("%s - %s updated" % (clean_row["reporting_month"], clean_row["supplier_name"]))
                except ObjectDoesNotExist, exception:
                    logger.error("%s-%s" % (exception, clean_row["supplier_name"]))
                    break


if __name__ == '__main__':
    task_run = LoadMonthlyEnforcementStats()
    task_run._init()
    print "\nTask finished at %s\n" % str(datetime.datetime.now())
