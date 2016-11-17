from __future__ import division
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
import csv
from csvkit.utilities.in2csv import In2CSV
import re
import logging
import time
import datetime
import requests
from dateutil.parser import parse
from collections import OrderedDict
import sys
import os.path

logger = logging.getLogger("cali_water_reports")

class MonthlyFormattingMethods(object):
    """
    scaffolding used when dealing with state water board data
    """

    def _can_write_excel_file_from(self, file_name, excel_file_url, file_download_excel_path):
        """
        can I write an excel file from url
        """
        try:
            logger.debug("Requesting %s" % (file_name))
            response = requests.get(excel_file_url, headers=settings.REQUEST_HEADERS)
            with open(file_download_excel_path, "w+", buffering=-1) as output_file:
                output_file.write(response.content)
                excel_file_exists = os.path.isfile(file_download_excel_path)
                excel_file_size = os.path.getsize(file_download_excel_path)
                if excel_file_exists == True and excel_file_size > 0:
                    logger.debug("Success!")
        except Exception, exception:
            logger.error(exception)
            raise

    def _can_convert_excel_file_to(self, file_name, file_created_csv_path, file_download_excel_path):
        """
        """
        try:
            logger.debug("Converting %s to %s" % (file_name, file_created_csv_path))
            args = ["-f", "xlsx", file_download_excel_path]
            with open(file_created_csv_path, "w+", buffering=-1) as output_file:
                utility = In2CSV(args, output_file).main()
                csv_file_exists = os.path.isfile(file_created_csv_path)
                csv_file_size = os.path.getsize(file_created_csv_path)
                if csv_file_exists == True and csv_file_size > 0:
                    logger.debug("Success!")
        except Exception, exception:
            logger.error(exception)
            raise


    def _can_create_hydrologic_region_slug(self, item):
        """
        """
        value = item.encode("ascii", "ignore").lower().strip().replace(" ", "-")
        value = re.sub(r"[^\w-]", "", value)
        return value


    def _can_prettify_and_slugify_string(self, string):
        """
        """
        more_than_one_space = re.compile("\s+")
        string = string.lower()
        value = re.sub("[^0-9a-zA-Z\s-]+", " ", string)
        city_in = "city" in value
        town_in = "town" in value
        if city_in == True:
            start_city_check = re.compile("^city of")
            end_city_check = re.compile("city of")
            city_match = re.search(start_city_check, value)
            try:
                if city_match:
                    pretty_name = value
                else:
                    end_city_match = re.search(end_city_check, value)
                    if end_city_match:
                        value = value.split("city of")
                        pretty_name = "city of %s" % (value[0].strip())
                    else:
                        pretty_name = value
            except Exception, exception:
                logger.error(exception)
                raise
        elif town_in == True:
            start_town_check = re.compile("^town of")
            end_town_check = re.compile("town of")
            town_match = re.search(start_town_check, value)
            try:
                if town_match:
                    pretty_name = value
                else:
                    end_town_match = re.search(end_town_check, value)
                    if end_town_match:
                        value = value.split("town of")
                        pretty_name = "town of %s" % (value[0].strip())
                    else:
                        pretty_name = value
            except Exception, exception:
                logger.error(exception)
                raise
        else:
            pretty_name = value
        pretty_name = " ".join(pretty_name.split())
        if pretty_name == "san bernardino county service area 70j":
            pretty_name = "san bernardino county service area 70"
        slug = pretty_name.encode("ascii", "ignore").lower()
        slug = re.sub(r"[^a-z0-9]+", "-", slug).strip("-")
        slug = re.sub(r"[-]+", "-", slug)
        output = {"supplier_slug": slug, "supplier_name": pretty_name}
        return output


    def _can_convert_str_to_num(self, value):
        """
        can this value be converted to an int
        """
        status = {}
        # actually integer values
        if isinstance(value, (int, long)):
            status["convert"] = True
            status["value"] = value
        # some floats can be converted without loss
        elif isinstance(value, float):
            status["convert"] = (int(value) == float(value))
            status["value"] = value
        # we can't convert non-string
        elif not isinstance(value, basestring):
            status["convert"] = False
            status["value"] = None
        else:
            value = value.strip()
            try:
                # try to convert value to float
                float_value = float(value)
                status["convert"] = True
                status["value"] = float_value
            except ValueError:
                # if fails try to convert value to int
                try:
                    int_value = int(value)
                    status["convert"] = True
                    status["value"] = int_value
                # if fails it's a string
                except ValueError:
                    try:
                        int_value = int(value.replace(",", ""))
                        status["convert"] = True
                        status["value"] = int_value
                    except:
                        status["convert"] = False
                        status["value"] = None
        return status


    def _can_create_datetime_from_filename(self, file):
        """
        can I create a datetime out of the file name because there are six digits
        """
        file_name = os.path.basename(file)
        date_data = re.findall('([0-9]{6})[^0-9]', file_name)
        date_data = date_data[0]
        this_year = "20%s" % (date_data[4:])
        data_release = datetime.date(int(this_year), int(date_data[:2]), int(date_data[2:4]))
        if data_release > datetime.date(2014, 9, 01):
            return data_release


    def _can_make_string_to_datetime(self, date):
        """
        are the keys I expect to be in the file present
        """
        parsed_date = parse(date)
        return parsed_date


    def _can_make_xldate_to_datetime(self, excel_date):
        """
        """
        if excel_date.isdigit() == True:
            xldate = int(excel_date)
            baseline_datetime = datetime.datetime(1899, 12, 31)
            delta_time = datetime.timedelta(days = xldate)
            converted_date_time = baseline_datetime + delta_time
            converted_date = converted_date_time.date().replace(day = 1)
            if type(converted_date) == datetime.date and converted_date > datetime.date(2013, 9, 01):
                return converted_date


if __name__ == '__main__':
    task_run =  MonthlyFormattingMethods()
    logger.debug(dir(task_run))
    print "\nTask finished at %s\n" % str(datetime.datetime.now())
