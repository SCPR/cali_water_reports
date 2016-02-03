from django.test import TestCase
from django.conf import settings
import csv
from csvkit.utilities.in2csv import In2CSV
import re
import logging
import time
import datetime
import requests
from dateutil import parser
import os.path

logger = logging.getLogger("cali_water_reports")

# Create your tests here.
class TestFetchUsageStats(TestCase):
    """
    tests ability to download and process monthly usage stats
    """

    def setUp(self):

        self.excel_file_urls = [
            {"category": "usage", "file_url": settings.USAGE_FILE},
            {"category": "enforcement", "file_url": settings.ENFORCEMENT_FILE},
        ]

        self.file_name = None

        self.file_download_excel_path = None

        self.file_created_csv_path = None

        self.list_of_previous_files = [
            "http://www.waterboards.ca.gov/water_issues/programs/conservation_portal/docs/2015dec/uw_supplier_data120115.xlsx",
            "http://www.waterboards.ca.gov/waterrights/water_issues/programs/drought/docs/uw_supplier_data082715.xlsx",
            "http://www.waterboards.ca.gov/waterrights/water_issues/programs/drought/docs/uw_supplier_data073015.xlsx",
            "http://www.waterboards.ca.gov/waterrights/water_issues/programs/drought/docs/uw_supplier_data070115.xlsx"
            "http://www.waterboards.ca.gov/waterrights/water_issues/programs/drought/docs/060215uw_supplier_data.xlsx",
            "http://www.waterboards.ca.gov/waterrights/water_issues/programs/drought/docs/050515uw_supplier_data.xlsx",
            "http://www.swrcb.ca.gov/waterrights/water_issues/programs/drought/docs/uw_supplier_data040715.xlsx",
            "http://www.swrcb.ca.gov/waterrights/water_issues/programs/drought/docs/uw_supplier_data030315.xlsx",
            "http://www.swrcb.ca.gov/waterrights/water_issues/programs/drought/docs/uw_supplier_data020315.xlsx",
            "http://www.swrcb.ca.gov/waterrights/water_issues/programs/drought/docs/uw_supplier_data010215.xlsx",
            "http://www.swrcb.ca.gov/waterrights/water_issues/programs/drought/docs/uw_supplier_data120214.xlsx",
            "http://www.swrcb.ca.gov/waterrights/water_issues/programs/drought/docs/emergency_regulations/uw_supplier_data110414.xlsx",
            "http://www.swrcb.ca.gov/waterrights/water_issues/programs/drought/docs/uw_supplier_data100714.xlsx",
            "http://www.swrcb.ca.gov/waterrights/water_issues/programs/drought/docs/workshops/urban_water_conservation_mandatory_results091114.xlsx",
        ]

        self.list_of_usage_keys = [
            "Supplier Name",
            "Hydrologic Region",
            "Stage Invoked",
            "Mandatory Restrictions",
            "Reporting Month",
            "REPORTED Total Monthly Potable Water Production Reporting Month",
            "REPORTED Total Monthly Potable Water Production 2013",
            "REPORTED Units",
            "Qualification",
            "Total Population Served",
            "REPORTED Residential Gallons-per-Capita-Day (R-GPCD) (starting in September 2014)",
            "Optional - Enforcement Actions",
            "Optional - Implementation",
            "Optional - REPORTED Recycled Water",
            "CALCULATED Total Monthly Potable Water Production Reporting Month Gallons (Values calculated by Water Board staff. REPORTED Total Monthly Potable Water Production Reporting Month - REPORTED Monthly Ag Use Reporting Month; converted to gallons.)",
            "CALCULATED Total Monthly Potable Water Production 2013 Gallons (Values calculated by Water Board staff. REPORTED Total Monthly Potable Water Production 2013 - REPORTED Monthly Ag Use 2013; converted to gallons.)",
            "CALCULATED R-GPCD Reporting Month (Values calculated by Water Board staff using methodology available at http://www.waterboards.ca.gov/waterrights/water_issues/programs/drought/docs/ws_tools/guidance_estimate_res_gpcd.pdf)",
            "% Residential Use",
            "Comments/Corrections",
        ]

        self.list_of_enforcement_keys = [
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

        self.list_of_potential_slugs = [
            "Adelanto City of",
            "Alameda County Water District",
            "Alco Water Service",
            "Alhambra  City of",
            "Amador Water Agency",
            "American Canyon, City of",
            "Anaheim  City of",
            "Anderson, City of",
            "Antioch  City of",
            "Apple Valley Ranchos Water Company",
            "Arcadia  City of",
            "Arcata  City of",
            "Arroyo Grande  City of",
            "Arvin Community Services District",
            "Atascadero Mutual Water Company",
            "Atwater  City of",
            "Azusa  City of",
            "Bakersfield  City of",
            "Bakman Water Company",
            "Banning  City of",
            "Beaumont-Cherry Valley Water District",
            "Bella Vista Water District",
            "Bellflower-Somerset Mutual Water Company",
            "Benicia  City of",
            "Beverly Hills  City of",
            "Big Bear City Community Services District",
            "Blythe  City of",
            "Brawley  City of",
            "Brea  City of",
            "Brentwood  City of",
            "Buena Park  City of",
            "Burbank  City of",
            "Burlingame  City of",
            "Calaveras County Water District",
            "Calexico  City of",
            "California City  City of",
        ]


    def test_a_download_chain(self):
        for item in self.excel_file_urls:
            item["file_name"] = os.path.basename(item["file_url"])
            item["file_download_excel_path"] = "%s/%s" % (settings.FILE_DOWNLOAD_PATH, item["file_name"])
            item["file_created_csv_path"] = item["file_download_excel_path"].replace(".xlsx", ".csv")
            if item["category"] == "usage":
                item["expected_keys"] = self.list_of_usage_keys
            elif item["category"] == "enforcement":
                item["expected_keys"] = self.list_of_enforcement_keys
            self.Test_can_get_response_success_from_url(item)
            self.Test_can_write_excel_file_from(item)
            self.Test_can_convert_excel_file_to(item)
            self.Test_can_find_expected_keys(item)
            self.Test_can_make_string_to_datetime(item)


    def Test_can_get_response_success_from_url(self, item):
        """
        test if able to download report from url
        """
        response = requests.get(item["file_url"], headers=settings.REQUEST_HEADERS)
        self.assertEquals(response.status_code, 200)
        self.assertIsNotNone(response.content)


    def Test_can_write_excel_file_from(self, item):
        """
        test can I write an excel file from url
        """
        response = requests.get(item["file_url"], headers=settings.REQUEST_HEADERS)
        with open(item["file_download_excel_path"], "w+", buffering=-1) as output_file:
            output_file.write(response.content)
            excel_file_exists = os.path.isfile(item["file_download_excel_path"])
            excel_file_size = os.path.getsize(item["file_download_excel_path"])
            self.assertEquals(excel_file_exists, True)
            self.assertTrue(excel_file_size > 0)


    def Test_can_convert_excel_file_to(self, item):
        """
        can I make an excel file out of this
        """
        args = ["-f", "xlsx", item["file_download_excel_path"]]
        with open(item["file_created_csv_path"], "w+", buffering=-1) as output_file:
            utility = In2CSV(args, output_file).main()
            csv_file_exists = os.path.isfile(item["file_created_csv_path"])
            csv_file_size = os.path.getsize(item["file_created_csv_path"])
            self.assertEquals(csv_file_exists, True)
            self.assertTrue(csv_file_size > 0)


    def Test_can_find_expected_keys(self, item):
        """
        are the keys I expect to be in the file present
        """
        num_of_expected_keys = len(item["expected_keys"])
        with open(item["file_created_csv_path"], "rb") as csvfile:
            csv_data = csv.DictReader(csvfile, delimiter=',')
            list_of_downloaded_keys = csv_data.next()
            num_of_downloaded_keys = len(list_of_downloaded_keys)
            self.assertTrue(num_of_expected_keys <= num_of_downloaded_keys)
            for key in item["expected_keys"]:
                self.assertTrue(list_of_downloaded_keys.has_key(key))


    def Test_can_make_string_to_datetime(self, item):
        """
        are the keys I expect to be in the file present
        """
        with open(item["file_created_csv_path"], "rb") as csvfile:
            csv_data = csv.DictReader(csvfile, delimiter=',')
            for row in csv_data:
                clean_row = {re.sub(r"\([^)]*\)", "", k).strip().replace("-", "").replace("  ", "").replace(" ", "_").replace("/", "_").lower(): v.strip() for k, v in row.iteritems()}
                self.assertTrue(clean_row.has_key("reporting_month"))
                datetime_key = clean_row["reporting_month"]
                parsed_date = parser.parse(datetime_key)
                self.assertIs(type(parsed_date), datetime.datetime)
                self.assertTrue(parsed_date > datetime.datetime(2013, 9, 01))


    def test_can_create_hydrologic_region_slug(self):
        """
        """
        for string in self.list_of_potential_slugs:
            slug = string.encode("ascii", "ignore").lower().strip()
            slug = re.sub(r"[^a-z0-9]+", "-", slug).strip("-")
            slug = re.sub(r"[-]+", "-", slug)
            self.assertIsNotNone(slug)


    def test_can_prettify_and_slugify_string(self):
        """
        convert a water supplier name to a slug
        """
        more_than_one_space = re.compile("\s+")
        for string in self.list_of_potential_slugs:
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
            slug = pretty_name.encode("ascii", "ignore").lower().strip()
            slug = re.sub(r"[^a-z0-9]+", "-", slug).strip("-")
            slug = re.sub(r"[-]+", "-", slug)
            output = {"slug": slug, "pretty_name": pretty_name}
            self.assertIsNotNone(output)
            self.assertIs(type(output), dict)


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


    def test_can_create_datetime_from_filename(self):
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


    def _test_can_make_xldate_to_datetime(self):
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


    def _test_can_build_model_instance(self):
        with open(self.file_created_csv_path, "rb") as csvfile:
            csv_data = csv.DictReader(csvfile, delimiter=',')
            for row in csv_data:
                clean_row = {re.sub(r"\([^)]*\)", "", k).strip().replace("-", "").replace("  ", "").replace(" ", "_").replace("/", "_").lower(): v.strip() for k, v in row.iteritems()}
                self.assertIsNotNone(clean_row)
                self.assertIs(type(clean_row), dict)


    def _test_can_make_supplier(self):
        """
        """
        logger.debug("pass for now")


    def _test_can_make_supplier_month_record(self):
        """
        """
        logger.debug("pass for now")
