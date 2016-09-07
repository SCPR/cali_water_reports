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
from dateutil import parser
from collections import OrderedDict
import sys
import os.path

logger = logging.getLogger("cali_water_reports")

class TasksForMonthlyWaterUseReport(object):

    sluggy = MonthlyFormattingMethods()

    csv_file = "/Users/ckeller/Desktop/stress_test_fields.csv"

    def _init(self, *args, **kwargs):
        # self.model_second_round_reductions(self.csv_file)
        # self.model_cum_savings(self.csv_file)
        # self.model_supplier_reached_target()
        self.model_supplier_stress_test(self.csv_file)

    def model_supplier_stress_test(self, target_csv_file):
        with open(target_csv_file, "rb") as csvfile:
            csv_data = csv.DictReader(csvfile, delimiter=',')
            for row in csv_data:
                clean_row = {re.sub(r"\([^)]*\)", "", k).strip().replace("- ", "").replace(" ", "_").replace("/", "_").lower(): v.strip() for k, v in row.iteritems()}
                clean_row["supplier_name"] = clean_row["supplier_name"].split(" (")
                supplier = self.sluggy._can_prettify_and_slugify_string(clean_row["supplier_name"][0])
                clean_row["supplier_name"] = supplier["supplier_name"]
                clean_row["supplier_slug"] = supplier["supplier_slug"]
                try:
                    supplier = WaterSupplier.objects.filter(supplier_slug=clean_row["supplier_slug"]).first()
                    if supplier:
                        supplier.stress_test_conservation_standard = clean_row["stress_test_conservation_standard"]
                        supplier.save()
                except Exception, exception:
                    error_output = "%s %s" % (exception, clean_row["supplier_slug"])
                    logger.error(error_output)
                    raise

    def model_second_round_reductions(self, target_csv_file):
        with open(target_csv_file, "rb") as csvfile:
            csv_data = csv.DictReader(csvfile, delimiter=',')
            for row in csv_data:
                clean_row = {re.sub(r"\([^)]*\)", "", k).strip().replace("- ", "").replace(" ", "_").replace("/", "_").lower(): v.strip() for k, v in row.iteritems()}
                supplier = self.sluggy._can_prettify_and_slugify_string(clean_row["supplier_name"])
                clean_row["supplier_name"] = supplier["supplier_name"]
                clean_row["supplier_slug"] = supplier["supplier_slug"]
                float_value = self.sluggy._can_convert_str_to_num(clean_row["new_conservation_standard"])
                clean_row["float_conservation_standard"] = float_value["value"]
                supplier = WaterSupplier.objects.filter(supplier_slug=supplier["supplier_slug"])
                for item in supplier:
                    try:
                        item.march_1_reduction = clean_row["float_conservation_standard"]
                        item.save()
                    except Exception, exception:
                        error_output = "%s %s" % (exception, clean_row["supplier_slug"])
                        logger.error(error_output)
                        raise

    def model_cum_savings(self, target_csv_file):
        with open(target_csv_file, "rb") as csvfile:
            csv_data = csv.DictReader(csvfile, delimiter=',')
            for row in csv_data:
                clean_row = {re.sub(r"\([^)]*\)", "", k).strip().replace("- ", "").replace(" ", "_").replace("/", "_").lower(): v.strip() for k, v in row.iteritems()}
                supplier = self.sluggy._can_prettify_and_slugify_string(clean_row["supplier_name"])
                clean_row["supplier_name"] = supplier["supplier_name"]
                clean_row["supplier_slug"] = supplier["supplier_slug"]
                clean_row["missed_reduction_target_by"] = float(clean_row["missed_reduction_target_by"])
                clean_row["cumulative_percent_saved"] = float(clean_row["cumulative_percent_saved"])
                supplier = WaterSupplier.objects.filter(supplier_slug=supplier["supplier_slug"])
                for item in supplier:
                    try:
                        item.cumulative_percent_saved  = clean_row["cumulative_percent_saved"]
                        item.missed_reduction_target_by = clean_row["missed_reduction_target_by"]
                        item.compliance_priority = clean_row["compliance_priority"]
                        item.category_definition = clean_row["category_definition"]
                        item.save()
                    except Exception, exception:
                        error_output = "%s %s" % (exception, clean_row["supplier_slug"])
                        logger.error(error_output)
                        raise


    def model_supplier_reached_target(self):
        """
        """
        suppliers = WaterSupplier.objects.all()
        for supplier in suppliers:
            try:
                if supplier.missed_reduction_target_by == None:
                    supplier.reached_initial_reduction_target = False
                elif supplier.missed_reduction_target_by > 0:
                    supplier.reached_initial_reduction_target = False
                elif supplier.missed_reduction_target_by < 0:
                        supplier.reached_initial_reduction_target = True
                else:
                    supplier.reached_initial_reduction_target = False
                supplier.save()
            except Exception, exception:
                error_output = "%s %s" % (exception, supplier.supplier_slug)
                logger.error(error_output)
                raise


    """
    OLD AND OBSOLTETE FUNCTIONS
    """
    def add_monthly_production_stats_to_water_supplier(self):
            queryset = WaterSupplier.objects.all()
            for item in queryset:

                logger.debug(item.supplier_slug)

                production_numbers_list = []

                latest_month_reports = WaterSupplierMonthlyReport.objects.filter(report_date = "2015-07-01").filter(supplier_slug = item.supplier_slug).order_by("reporting_month")

                for report in latest_month_reports:
                    data_dict = {}
                    data_dict["month"] = report.reporting_month.month
                    data_dict["prod_gallons"] = report.calculated_production_monthly_gallons_month_2013
                    production_numbers_list.append(data_dict)

                logger.debug(production_numbers_list)

                if production_numbers_list != None:
                    item.production_2013_june = self.return_prod_gallons(production_numbers_list, 6)
                    item.production_2013_july = self.return_prod_gallons(production_numbers_list, 7)
                    item.production_2013_aug = self.return_prod_gallons(production_numbers_list, 8)
                    item.production_2013_sept = self.return_prod_gallons(production_numbers_list, 9)
                    item.production_2013_oct = self.return_prod_gallons(production_numbers_list, 10)
                    item.production_2013_nov = self.return_prod_gallons(production_numbers_list, 11)
                    item.production_2013_dec = self.return_prod_gallons(production_numbers_list, 12)
                    item.production_2013_jan = self.return_prod_gallons(production_numbers_list, 1)
                    item.production_2013_feb = self.return_prod_gallons(production_numbers_list, 2)
                    item.save()
                else:
                    logger.debug("Something is wrong")
                    raise


    def return_prod_gallons(self, list, month):
        match = next((l for l in list if l["month"] == month), None)
        if match != None:
            output = match["prod_gallons"]
        else:
            output = None
        return output


    def add_hydrologic_region_to_watersuppliermonthlyreport(self):
        queryset = WaterSupplierMonthlyReport.objects.all()
        for item in queryset:
            if item.hydrologic_region == None:
                parent_obj = WaterSupplier.objects.get(supplier_name = item.supplier_name_id)
                item.hydrologic_region = parent_obj.hydrologic_region
                logger.debug(item.hydrologic_region)
                item.save()
            else:
                logger.debug("Everything's cool!")


    def add_hydrologic_region_slug_to_watersuppliermonthlyreport(self):
        queryset = WaterSupplierMonthlyReport.objects.all()
        for item in queryset:
            if item.hydrologic_region_slug == None:
                parent_obj = WaterSupplier.objects.get(supplier_name = item.supplier_name_id)
                item.hydrologic_region_slug = self._slug_a_string(item.hydrologic_region)
                logger.debug(item.hydrologic_region_slug)
                item.save()
            else:
                logger.debug("Everything's cool!")


    def add_supplier_slug_to_watersuppliermonthlyreport(self):
        queryset = WaterSupplierMonthlyReport.objects.all()
        for item in queryset:
            if item.supplier_slug == None:
                item.supplier_slug = self._slug_a_string(item.supplier_name_id)
                logger.debug(item.supplier_slug)
                #item.save()
            else:
                logger.debug("Everything's cool!")


    def fix_dates_on_reports(self):
        queryset = WaterSupplierMonthlyReport.objects.filter(report_date = "2015-04-07")
        for item in queryset:
            output = datetime.date(item.reporting_month.year, item.reporting_month.month, 01)
            item.reporting_month = output
            logger.debug(item.reporting_month)
            item.save()


    def model_first_and_second_reduction_proposals(self):
        suppliers = WaterSupplier.objects.all()
        queryset = WaterSupplierMonthlyReport.objects.filter(report_date = "2015-04-07")
        new_queries = QueryUtilities()
        all_months_latest_report = new_queries._all_months_latest_report(queryset)
        for supplier in suppliers:
            results = all_months_latest_report.filter(supplier_name_id = supplier.supplier_name)
            this_supplier_set = results.filter(Q(reporting_month = "2014-07-01") | Q(reporting_month = "2014-08-01") | Q(reporting_month = "2014-09-01"))
            if len(this_supplier_set) > 0:
                three_month_rgcpd = new_queries._get_rolling_avg_rgcpd(this_supplier_set)
            else:
                three_month_rgcpd = None
            april_7_tier = new_queries._get_conservation_tier(this_supplier_set)
            april_18_tier = new_queries._get_second_draft_conservation_tier(three_month_rgcpd)
            supplier.april_7_tier = april_7_tier["conservation_tier"]
            supplier.april_7_reduction = april_7_tier["conservation_standard"]
            supplier.april_7_rgpcd = april_7_tier["conservation_placement"]
            supplier.april_18_tier = april_18_tier["conservation_tier"]
            supplier.april_18_reduction = april_18_tier["conservation_standard"]
            supplier.april_18_rgpcd = april_18_tier["conservation_placement"]
            supplier.save()


    def model_third_reduction_proposals(self, created_csv_file):
        sluggy = BuildMonthlyWaterUseReport()
        with open(created_csv_file, "rb") as csvfile:
            csv_data = csv.DictReader(csvfile, delimiter=',')
            for row in csv_data:
                as_decimal = row["conservation_standard"].replace("%", "")
                as_decimal = int(as_decimal) / 100
                rgpcd = float(row["jul_sep_2014_rgpcd"])
                supplier_formal = sluggy._prettify_and_slugify(row["supplier_name"])
                if supplier_formal[0] != None:
                    supplier = WaterSupplier.objects.filter(supplier_slug = supplier_formal[0])
                    for item in supplier:
                        item.april_28_tier = row["tier"]
                        item.april_28_reduction = as_decimal
                        item.april_28_rgpcd = row["jul_sep_2014_rgpcd"]
                        item.save()


    def model_june_5_reduction_proposals(self, created_csv_file):
        sluggy = BuildMonthlyWaterUseReport()
        with open(created_csv_file, "rb") as csvfile:
            csv_data = csv.DictReader(csvfile, delimiter=',')
            for row in csv_data:
                as_decimal = row["conservation_standard"].replace("%", "")
                as_decimal = int(as_decimal) / 100

                try:
                    rgpcd = float(row["jul_sep_2014_rgpcd"])
                except:
                    rgpcd = None

                row["supplier_name"] = row["supplier_name"].replace("Dist.", "District")
                row["supplier_name"] = row["supplier_name"].replace("Co.", "Company")
                supplier_formal = sluggy._prettify_and_slugify(row["supplier_name"])
                if supplier_formal[0] != None:
                    supplier = WaterSupplier.objects.filter(supplier_slug = supplier_formal[0])
                    for item in supplier:
                        try:
                            item.june_5_tier = row["tier"]
                            item.june_5_reduction = as_decimal
                            item.june_5_rgpcd = rgpcd
                            item.june_5_status = row["status"]
                            item.save()
                        except Exception, exception:
                            error_output = "%s %s" % (exception, row["jul_sep_2014_rgpcd"])
                            logger.error(error_output)
                            raise


    def model_june_11_reduction_proposals(self, created_csv_file):
        sluggy = BuildMonthlyWaterUseReport()
        with open(created_csv_file, "rb") as csvfile:
            csv_data = csv.DictReader(csvfile, delimiter=',')
            for row in csv_data:
                clean_row = {k.strip(): v.strip() for k, v in row.iteritems()}
                as_decimal = clean_row["conservation_standard"].replace("%", "")
                as_decimal = self._int_a_string(as_decimal)
                as_decimal = int(as_decimal) / 100
                try:
                    rgpcd = float(clean_row["jul_sep_2014_rgpcd"])
                except:
                    rgpcd = None
                clean_row["supplier_name"] = clean_row["supplier_name"].replace("Dist.", "District")
                clean_row["supplier_name"] = clean_row["supplier_name"].replace("Co.", "Company")
                supplier_formal = sluggy._prettify_and_slugify(clean_row["supplier_name"])
                june_11_estimated_savings = clean_row["estimated_savings"]
                if supplier_formal[0] != None:
                    supplier = WaterSupplier.objects.filter(supplier_slug = supplier_formal[0])
                    for item in supplier:
                        try:
                            item.june_11_tier = clean_row["tier"]
                            item.june_11_reduction = as_decimal
                            item.june_11_rgpcd = rgpcd
                            item.june_11_status = clean_row["status"]
                            item.june_11_estimated_savings = june_11_estimated_savings
                            item.save()
                        except Exception, exception:
                            error_output = "%s %s" % (exception, row["jul_sep_2014_rgpcd"])
                            logger.error(error_output)
                            raise


    def model_monthly_enforcement_stats(self, created_csv_file):

        list_enforcement_keys = [
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
            "Enforcement Comments"
        ]

        proceed = {}

        sluggy = BuildMonthlyWaterUseReport()

        with open(created_csv_file, "rb") as csvfile:
            csv_data = csv.reader(csvfile, delimiter=',')
            list_downloaded_headers = csv_data.next()
            num_downloaded_keys = len(list_downloaded_headers)
            num_expected_keys = len(list_enforcement_keys)
            if num_downloaded_keys == num_expected_keys:
                proceed["status"] = sluggy._compare_lists(list_downloaded_headers, list_enforcement_keys)
                proceed["column_structure"] = list_downloaded_headers
            else:
                proceed["status"] = False
                proceed["column_structure"] = None
        if proceed["status"] == True:
            print "COLUMN HEADERS CHECK OUT: I can process %s" % (created_csv_file)
            data_release = created_csv_file.replace("/Users/ckeller/Desktop/", "")
            data_release = data_release.replace("enforcement_statistics.csv", "")
            this_year = "20%s" % (data_release[4:])
            data_release = datetime.date(int(this_year), int(data_release[:2]), int(data_release[2:4]))
            with open(created_csv_file, "rb") as csvfile:
                csv_data = csv.DictReader(csvfile, delimiter=',')
                for row in csv_data:
                    clean_row = {k.strip(): v.strip() for k, v in row.iteritems()}
                    try:
                        raw_dates = clean_row["Reporting Month"].split("-")
                        my_reporting_month = "20%s-%s-%s" % (raw_dates[1], raw_dates[0], 01)
                        my_reporting_month = parser.parse(my_reporting_month)
                    except:
                        try:
                            my_reporting_month = "20%s-%s-%s" % (raw_dates[0], raw_dates[1], 01)
                            my_reporting_month = parser.parse(my_reporting_month)
                        except Exception, exception:
                            error_output = "%s %s" % (exception, clean_row["Reporting Month"])
                            logger.error(error_output)
                            raise
                    try:
                        supplier_formal = sluggy._prettify_and_slugify(row["Supplier Name"])
                        obj, created = WaterEnforcementMonthlyReport.objects.get_or_create(
                            report_date = data_release,
                            supplier_name = supplier_formal[1],
                            reporting_month = my_reporting_month,
                            defaults = {
                                "reported_to_state_date": my_reporting_month,
                                "supplier_slug": supplier_formal[0],
                                "hydrologic_region": clean_row["Hydrologic Region"],
                                "hydrologic_region_slug": self._slug_a_string(clean_row["Hydrologic Region"]),
                                "enforcement_comments": clean_row["Enforcement Comments"],
                                "mandatory_restrictions": clean_row["Mandatory Restrictions"],
                                "total_population_served": self._int_a_string(clean_row["Population Served"]),
                                "supplier_id": None,
                                "water_days_allowed_week": self._int_a_string(clean_row["Water Days Allowed/Week"]),
                                "complaints_received": self._int_a_string(clean_row["Complaints Received"]),
                                "follow_up_actions": self._int_a_string(clean_row["Follow-up Actions"]),
                                "warnings_issued": self._int_a_string(clean_row["Warnings Issued"]),
                                "penalties_assessed": self._int_a_string(clean_row["Penalties Assessed"]),
                            }
                        )
                        if not created:
                            logger.debug("%s - %s exists" % (supplier_formal[1], my_reporting_month))
                        elif created:
                            logger.debug("%s - %s created" % (supplier_formal[1], my_reporting_month))
                    except ObjectDoesNotExist, exception:
                        logger.error("%s %s" % (exception, supplier_formal[1]))
                        raise
        else:
            print "ISSUE WITH COLUMN HEADERS: I can not process %s" % (created_csv_file)


    def _int_a_string(self, string):
        string = string.strip()
        string = string.replace(",", "")
        try:
            if string == "" or string == None :
                output = 0
            else:
                output = int(string)
            return output
        except Exception, exception:
            print "%s - %s" % (exception, string)


    def _slug_a_string(self, string):
        value = string.encode("ascii", "ignore").lower().strip().replace(" ", "-")
        value = re.sub(r"[^\w-]", "", value)
        return value


if __name__ == '__main__':
    task_run = TasksForMonthlyWaterUseReport()
    task_run._init()
    print "\nTask finished at %s\n" % str(datetime.datetime.now())
