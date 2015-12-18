from django.test import TestCase
from django.conf import settings
import csv
from csvkit.utilities.in2csv import In2CSV
import re
import logging
import time
import datetime
import requests
import os.path

logger = logging.getLogger("cali_water_reports")

# Create your tests here.
class TestFetchEnforcementStats(TestCase):
    """
    tests ability to download and process monthly enforcement stats
    """

    def setUp(self):

        self.excel_file_url = settings.ENFORCEMENT_FILE

        self.file_name = os.path.basename(self.excel_file_url)

        self.file_download_excel_path = "%s/%s" % (settings.FILE_DOWNLOAD_PATH, self.file_name)

        self.file_created_csv_path = self.file_download_excel_path.replace(".xlsx", ".csv")

        self.list_of_expected_keys = [
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

        self.list_of_potential_ints = [
            "This Could",
            " This Could ",
            "2,354",
            " 2,354 ",
            2354,
            "235,409",
            " 235,409 ",
            235409,
            3.1415,
            " 3.1415 ",
            -1,
            "42262",
            42262,
            "5060.7",
            5060.7,
            "6528.4",
            6528.4,
            "1001.5",
            1001.5,
            "221.27",
            221.27,
            "472853",
            472853,
            "237081000",
            237081000,
            "237,081,000",
            "61",
            "65.65",
            "75.27",
            "0.0343",
            0.0343,
            {"nonstring": "none"}
        ]

    def test_a_download_chain(self):
        self.Test_can_get_response_success_from_url()
        self.Test_can_write_excel_file_from()
        self.Test_can_convert_excel_file_to()
        self.Test_can_find_expected_keys()


    def Test_can_get_response_success_from_url(self):
        """
        test if able to download report from url
        """
        response = requests.get(self.excel_file_url, headers=settings.REQUEST_HEADERS)
        self.assertEquals(response.status_code, 200)
        self.assertIsNotNone(response.content)


    def Test_can_write_excel_file_from(self):
        """
        test can I write an excel file from url
        """
        response = requests.get(self.excel_file_url, headers=settings.REQUEST_HEADERS)
        with open(self.file_download_excel_path, "w+", buffering=-1) as output_file:
            output_file.write(response.content)
            excel_file_exists = os.path.isfile(self.file_download_excel_path)
            excel_file_size = os.path.getsize(self.file_download_excel_path)
            self.assertEquals(excel_file_exists, True)
            self.assertTrue(excel_file_size > 0)


    def Test_can_convert_excel_file_to(self):
        """
        can I make an excel file out of this
        """
        args = ["-f", "xlsx", self.file_download_excel_path]
        with open(self.file_created_csv_path, "w+", buffering=-1) as output_file:
            utility = In2CSV(args, output_file).main()
            csv_file_exists = os.path.isfile(self.file_created_csv_path)
            csv_file_size = os.path.getsize(self.file_created_csv_path)
            self.assertEquals(csv_file_exists, True)
            self.assertTrue(csv_file_size > 0)


    def Test_can_find_expected_keys(self):
        """
        are the keys I expect to be in the file present
        """
        num_of_expected_keys = len(self.list_of_expected_keys)
        with open(self.file_created_csv_path, "rb") as csvfile:
            csv_data = csv.DictReader(csvfile, delimiter=',')
            list_of_downloaded_keys = csv_data.next()
            num_of_downloaded_keys = len(list_of_downloaded_keys)
            self.assertTrue(num_of_expected_keys < num_of_downloaded_keys)
            # self.assertEquals(set(self.list_of_expected_keys), set(list_of_downloaded_keys))
            for key in self.list_of_expected_keys:
                self.assertTrue(list_of_downloaded_keys.has_key(key))


    def test_can_convert_str_to_num(self):
        """
        can this value be converted to an int
        http://stackoverflow.com/a/16464365
        """
        for value in self.list_of_potential_ints:

            status = {}

            # actually integer values
            if isinstance(value, (int, long)):
                status["convert"] = True
                status["value"] = value
                self.assertIs(type(value), int)
                self.assertEqual(status["convert"], True)

            # some floats can be converted without loss
            elif isinstance(value, float):
                status["convert"] = (int(value) == float(value))
                status["value"] = value
                self.assertEqual(status["convert"], False)

            # we can't convert non-string
            elif not isinstance(value, basestring):
                status["convert"] = False
                status["value"] = "Nonstring"
                self.assertEqual(status["convert"], False)

            else:
                value = value.strip()
                try:
                    # try to convert value to float
                    float_value = float(value)
                    status["convert"] = True
                    status["value"] = float_value
                    self.assertIs(type(float_value), float)
                    self.assertEqual(status["convert"], True)
                except ValueError:
                    # if fails try to convert value to int
                    try:
                        int_value = int(value)
                        status["convert"] = True
                        status["value"] = int_value
                        self.assertIs(type(int_value), int)
                        self.assertEqual(status["convert"], True)
                    # if fails it's a string
                    except ValueError:
                        status["convert"] = False
                        status["value"] = "String"
                        self.assertIs(type(value), str)
                        self.assertEqual(status["convert"], False)

            self.assertIsNotNone(status)
            self.assertIs(type(status), dict)
            self.assertEqual(status.has_key("convert"), True)
            self.assertEqual(status.has_key("value"), True)


    def _test_can_create_datetime_from_filename(self):
        """
        can I create a datetime out of the file name because there are six digits
        """
        for file in self.list_of_previous_files:
            file_name = os.path.basename(file)
            date_data = re.findall('([0-9]{6})[^0-9]', file_name)
            date_data = date_data[0]
            this_year = "20%s" % (date_data[4:])
            self.data_release = datetime.date(int(this_year), int(date_data[:2]), int(date_data[2:4]))

            # did we create a date
            self.assertIs(type(self.data_release), datetime.date)

            # is the date newer than Sept. 2014
            self.assertTrue(self.data_release > datetime.date(2014, 9, 01))


    def test_can_make_xldate_to_datetime(self):
        """
        can I create a datetime from a reporting month value
        """
        with open(self.file_created_csv_path, "rb") as csvfile:
            csv_data = csv.DictReader(csvfile, delimiter=',')
            for row in csv_data:

                # is our target key in the dictionary
                clean_row = {re.sub(r"\([^)]*\)", "", k).strip().replace("-", "").replace("  ", "").replace(" ", "_").replace("/", "_").lower(): v.strip() for k, v in row.iteritems()}
                self.assertTrue(clean_row.has_key("reporting_month"))

                # is the value of our target key an integer
                datetime_key = clean_row["reporting_month"]
                self.assertTrue(datetime_key.isdigit())

                # when we convert it over, is it a date?
                xldate = int(clean_row["reporting_month"])
                baseline_datetime = datetime.datetime(1899, 12, 31)
                delta_time = datetime.timedelta(days = xldate)
                converted_date_time = baseline_datetime + delta_time
                self.assertIs(type(converted_date_time), datetime.datetime)

                # is the date newer than Sept. 2013
                self.assertTrue(converted_date_time > datetime.datetime(2013, 9, 01))
