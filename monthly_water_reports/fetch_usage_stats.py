from __future__ import division
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from monthly_water_reports.models import WaterSupplier, WaterSupplierMonthlyReport
from fetch_methods import MonthlyFormattingMethods
import csv
from csvkit.utilities.in2csv import In2CSV
import re
import logging
import time
import datetime
import requests
from dateutil import parser
from collections import OrderedDict
import sys
import os.path
import shutil

logger = logging.getLogger("cali_water_reports")

class BuildMonthlyWaterUseReport(object):
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
        "Hydrologic Region",
        "Stage Invoked",
        "Mandatory Restrictions",
        "Reporting Month",
        "REPORTED Total Monthly Potable Water Production 2014/2015",
        "REPORTED Total Monthly Potable Water Production 2013",
        "REPORTED Units",
        "Qualification",
        "Total Population Served",
        "REPORTED Residential Gallons-per-Capita-Day (R-GPCD) (starting in September 2014)",
        "Optional - Enforcement Actions",
        "Optional - Implementation",
        "Optional - REPORTED Recycled Water",
        "CALCULATED Total Monthly Potable Water Production 2014/2015 Gallons (Values calculated by Water Board staff. REPORTED Total Monthly Potable Water Production 2014/2015 - REPORTED Monthly Ag Use 2014/2015; converted to gallons.)",
        "CALCULATED Total Monthly Potable Water Production 2013 Gallons (Values calculated by Water Board staff. REPORTED Total Monthly Potable Water Production 2013 - REPORTED Monthly Ag Use 2013; converted to gallons.)",
        "CALCULATED R-GPCD 2014/2015 (Values calculated by Water Board staff using methodology available at http://www.waterboards.ca.gov/waterrights/water_issues/programs/drought/docs/ws_tools/guidance_estimate_res_gpcd.pdf)",
        "% Residential Use",
        "Comments/Corrections",
    ]

    suppliers_to_skip = [
        "city-of-coalinga",
        "mountain-house-community-services-district"
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

                data_to_process = {}

                data_to_process["supplier_name"] = supplier_formatted["supplier_name"]

                data_to_process["supplier_slug"] = supplier_formatted["supplier_slug"]

                data_to_process["supplier_url"] = None

                data_to_process["supplier_mwd_member"] = False

                try:
                    data_to_process["hydrologic_region"] = clean_row["hydrologic_region"]
                    data_to_process["hydrologic_region_slug"] = self.sluggy._can_create_hydrologic_region_slug(clean_row["hydrologic_region"])
                except Exception, exception:
                    error_output = "%s %s" % (exception, clean_row["hydrologic_region"])
                    logger.error(error_output)
                    raise

                data_to_process["created_date"] = datetime.datetime.now()

                data_to_process["supplier_notes"] = None

                data_to_process["stage_invoked"] = clean_row["stage_invoked"]

                if clean_row["mandatory_restrictions"] == "Yes":
                    data_to_process["mandatory_restrictions"] = True
                else:
                    data_to_process["mandatory_restrictions"] = False

                data_to_process["enforcement_actions"] = clean_row["optional_enforcement_actions"]

                data_to_process["implementation"] = clean_row["optional_implementation"]

                data_to_process["recycled_water"] = clean_row["optional_reported_recycled_water"]

                # try:
                #     data_to_process["recycled_water_units"] = clean_row["recycled_water_units"]
                # except Exception, exception:
                data_to_process["recycled_water_units"] = None

                data_to_process["units"] = clean_row["reported_units"].upper()

                data_to_process["qualification"] = clean_row["qualification"]

                data_to_process["comments_or_corrections"] = clean_row["comments_corrections"]

                try:
                    data_to_process["reporting_month"] = self.sluggy._can_make_string_to_datetime(clean_row["reporting_month"])
                except Exception, exception:
                    error_output = "%s %s" % (exception, clean_row)
                    logger.error(error_output)
                    raise

                reported_prod_2014_15 = clean_row["reported_total_monthly_potable_water_production_2014_2015"]
                try:
                    if self.sluggy._can_convert_str_to_num(reported_prod_2014_15)["convert"] == True:
                        data_to_process["total_monthly_potable_water_production_2014"] = self.sluggy._can_convert_str_to_num(reported_prod_2014_15)["value"]
                except Exception, exception:
                    error_output = "%s %s" % (exception, clean_row)
                    logger.error(error_output)
                    raise

                reported_prod_2013 = clean_row["reported_total_monthly_potable_water_production_2013"]
                try:
                    if self.sluggy._can_convert_str_to_num(reported_prod_2013)["convert"] == True:
                        data_to_process["total_monthly_potable_water_production_2013"] = self.sluggy._can_convert_str_to_num(reported_prod_2013)["value"]
                except Exception, exception:
                    error_output = "%s %s" % (exception, clean_row)
                    logger.error(error_output)
                    raise

                try:
                    if self.sluggy._can_convert_str_to_num(clean_row["total_population_served"])["convert"] == True:
                        data_to_process["total_population_served"] = self.sluggy._can_convert_str_to_num(clean_row["total_population_served"])["value"]
                except Exception, exception:
                    error_output = "%s %s" % (exception, clean_row)
                    logger.error(error_output)
                    raise

                try:
                    if self.sluggy._can_convert_str_to_num(clean_row["%_residential_use"])["convert"] == True:
                        data_to_process["percent_residential_use"] = self.sluggy._can_convert_str_to_num(clean_row["%_residential_use"])["value"]
                        data_to_process["percent_residential_use"] = data_to_process["percent_residential_use"] / 100
                except Exception, exception:
                    error_output = "%s %s" % (exception, clean_row)
                    logger.error(error_output)
                    raise

                try:
                    if self.sluggy._can_convert_str_to_num(clean_row["reported_residential_gallons-per-capita-day"])["convert"] == True:
                        data_to_process["reported_rgpcd"] = self.sluggy._can_convert_str_to_num(clean_row["reported_residential_gallons-per-capita-day"])["value"]
                    else:
                        data_to_process["reported_rgpcd"] = None
                except Exception, exception:
                    data_to_process["reported_rgpcd"] = None
                    error_output = "%s %s" % (exception, clean_row)
                    logger.error(error_output)
                    raise

                try:
                    if self.sluggy._can_convert_str_to_num(clean_row["calculated_total_monthly_potable_water_production_2014_2015_gallons"])["convert"] == True:
                        data_to_process["calculated_production_monthly_gallons_month_2014"] = self.sluggy._can_convert_str_to_num(clean_row["calculated_total_monthly_potable_water_production_2014_2015_gallons"])["value"]
                except Exception, exception:
                    error_output = "%s %s" % (exception, clean_row)
                    logger.error(error_output)
                    raise

                try:
                    if self.sluggy._can_convert_str_to_num(clean_row["calculated_total_monthly_potable_water_production_2013_gallons"])["convert"] == True:
                        data_to_process["calculated_production_monthly_gallons_month_2013"] = self.sluggy._can_convert_str_to_num(clean_row["calculated_total_monthly_potable_water_production_2013_gallons"])["value"]
                except Exception, exception:
                    error_output = "%s %s" % (exception, clean_row)
                    logger.error(error_output)
                    raise

                try:
                    if self.sluggy._can_convert_str_to_num(clean_row["calculated_r-gpcd_2014_2015"])["convert"] == True:
                        data_to_process["calculated_rgpcd_2014"] = self.sluggy._can_convert_str_to_num(clean_row["calculated_r-gpcd_2014_2015"])["value"]
                except Exception, exception:
                    error_output = "%s %s" % (exception, clean_row)
                    logger.error(error_output)
                    raise

                # try:
                #     data_to_process["calculated_rgpcd_2013"] = self.sluggy._can_convert_str_to_num(clean_row["calculated_r-gpcd_2013"])["value"]
                # except Exception, exception:
                #     data_to_process["calculated_rgpcd_2013"] = None
                #     error_output = "%s %s" % (exception, clean_row)
                #     logger.error(error_output)
                #     raise

                try:
                    data_to_process["report_date"] = self.sluggy._can_create_datetime_from_filename(file_created_csv_path)
                except Exception, exception:
                    error_output = "%s %s" % (exception, clean_row)
                    logger.error(error_output)
                    raise

                self._save_supplier_instance_from(data_to_process)
                self._save_supplier_report_instance_from(data_to_process)


    def _save_supplier_instance_from(self, data):
        """
        save water supplier model instance from dictionary
        """
        try:
            if data["supplier_slug"] in self.suppliers_to_skip:
                pass
            else:
                obj, created = WaterSupplier.objects.get_or_create(
                    supplier_slug = data["supplier_slug"],
                    defaults = {
                        "supplier_name": data["supplier_name"],
                        "supplier_url": data["supplier_url"],
                        "supplier_mwd_member": data["supplier_mwd_member"],
                        "hydrologic_region": data["hydrologic_region"],
                        "hydrologic_region_slug": data["hydrologic_region_slug"],
                        "created_date": data["created_date"],
                        "supplier_notes": data["supplier_notes"],
                    }
                )
                if created:
                    logger.debug("%s created: %s - %s" % (data["supplier_name"], data["supplier_slug"], data["hydrologic_region"]))
                else:
                    logger.debug("%s exists" % (data["supplier_name"]))
        except ValueError, exception:
            traceback.print_exc(file=sys.stdout)
            error_output = "%s %s" % (exception, data)
            logger.error(error_output)
            raise


    def _save_supplier_report_instance_from(self, data):
        """
        save monthly water supplier model instance from dictionary
        """
        try:
            if data["supplier_slug"] in self.suppliers_to_skip:
                pass
            else:
                supplier = WaterSupplier.objects.get(supplier_slug = data["supplier_slug"])
                report, created = supplier.watersuppliermonthlyreport_set.get_or_create(
                    reporting_month = data["reporting_month"],
                    report_date = data["report_date"],
                    supplier_name = data["supplier_name"],
                    defaults = {
                        "supplier_slug": data["supplier_slug"],
                        "stage_invoked": data["stage_invoked"],
                        "mandatory_restrictions": data["mandatory_restrictions"],
                        "reporting_month": data["reporting_month"],
                        "total_monthly_potable_water_production_2014": data["total_monthly_potable_water_production_2014"],
                        "total_monthly_potable_water_production_2013": data["total_monthly_potable_water_production_2013"],
                        "units": data["units"].upper(),
                        "qualification": data["qualification"],
                        "total_population_served": data["total_population_served"],
                        "reported_rgpcd": data["reported_rgpcd"],
                        "enforcement_actions": data["enforcement_actions"],
                        "implementation": data["implementation"],
                        "recycled_water": data["recycled_water"],
                        "recycled_water_units": data["recycled_water_units"],
                        "calculated_production_monthly_gallons_month_2014": data["calculated_production_monthly_gallons_month_2014"],
                        "calculated_production_monthly_gallons_month_2013": data["calculated_production_monthly_gallons_month_2013"],
                        "calculated_rgpcd_2014": data["calculated_rgpcd_2014"],
                        # "calculated_rgpcd_2013": data["calculated_rgpcd_2013"],
                        "percent_residential_use": data["percent_residential_use"],
                        "comments_or_corrections": data["comments_or_corrections"],
                        "hydrologic_region": data["hydrologic_region"],
                        "hydrologic_region_slug": data["hydrologic_region_slug"],
                    }
                )
                if created:
                    logger.debug("%s created for %s" % (data["supplier_name"], data["reporting_month"]))
                else:
                    logger.debug("%s - %s exists" % (data["supplier_name"], data["reporting_month"]))
        except ObjectDoesNotExist, exception:
            traceback.print_exc(file=sys.stdout)
            error_output = "%s %s" % (exception, data)
            logger.error(error_output)


if __name__ == '__main__':
    task_run = BuildWaterUseReport()
    task_run._init()
    print "\nTask finished at %s\n" % str(datetime.datetime.now())
