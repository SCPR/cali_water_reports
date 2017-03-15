What is this?
=============

This Django project/application aims to answer the question "Is California water use increasing?" It processes the monthly water reports from California's [State Water Resources Control Board](http://www.waterboards.ca.gov/) and uses [django-bakery](https://django-bakery.readthedocs.io/en/latest/) to build KPCC's news application ["Is California water use increasing?"](http://projects.scpr.org/applications/monthly-water-use/)

There are three main steps to build the site you see [here](http://projects.scpr.org/applications/monthly-water-use/).

* [How We Process And Update Data Each Month](#how-we-process-and-update-data-each-month)
* [How We Build The Project Each Month](#how-we-build-the-project-each-month)
* [How We Deploy The Project Each Month](#how-we-deploy-the-project-each-month)

Table of Contents
=================

* [Assumptions](#assumptions)
* [Quickstart](#quickstart-to-get-up-and-running)
* [How We Process And Update Data Each Month](#how-we-process-and-update-data-each-month)
* [How We Build The Project Each Month](#how-we-build-the-project-each-month)
* [How We Deploy The Project Each Month](#how-we-deploy-the-project-each-month)
* [Available Fabric Commands](#available-fabric-commands)
* [Building a Mac OS Python dev environment](#building-a-mac-os-python-dev-environment)

Assumptions
===========

* You are running OSX.
* You are using Python 2.x
* You have [virtualenv](https://pypi.python.org/pypi/virtualenv) and [virtualenvwrapper](https://pypi.python.org/pypi/virtualenvwrapper) installed and working.
* You have MySQL installed

If any of these are not true, please skip ahead to [Building a Mac OS Python dev environment](#building-a-mac-os-python-dev-environment)

Quickstart To Get Up And Running
================================

* Clone this repo to wherever it is on your machine that you work on your projects

        git clone git@github.com:SCPR/cali_water_reports.git

* Change into that directory

        cd cali_water_reports

* Create your virtualenv and install the project/application requirements using pip

        mkvirtualenv cali_water_reports
        pip install -r requirements.txt

* Make a copy of ```TEMPLATE_development.yml``` and rename it to ```development.yml```

        cp TEMPLATE_development.yml development.yml

* Run ```fab makesecret``` and add the output on line 5 of ```development.yml```

        secret_key: "1=5avBguTW ... "

* Assuming MySQL is installed in ```development.yml``` add username and password for your MySQL install.

        database:
          host: "127.0.0.1"
          port: 3306
          database: "cali_water_reports"
          username: "root"
          password: ""

* Assuming you have virtualenv and pip installed run ```fab bootstrap```

    * This single fabric command uses several functions to scaffold the project by:
        * Creating the database: ```fab create_db```
        * Applying initial Django migrations: ```fab migrate```
        * Load initial data fixtures: ```fab load_fixtures```
        * Creating the Django superuser: ```python manage.py createsuperuser```
        * Running the Django development server: ```fab run```

* Navigate to ```http://127.0.0.1:8000/``` and you should arrive at the homepage that asks the question "Is California water use increasing?"

How We Process And Update Data Each Month
=========================================

Usually on the first Tuesday of the month California's [State Water Resources Control Board](http://www.waterboards.ca.gov/water_issues/programs/conservation_portal/conservation_reporting.shtml) will release the monthly reporting data from state water agencies.

The Excel files that make available have taken many shapes and forms over the past two years. The application as its currently constructed has successfully processed the Excel files for nearly a year. That said, at any moment the state may chance how structures the Excel files. And while tests exist to see if the latest file can be process, anticipating and abstracting out possible data formats is beyond the scope of this project.

To load the new supplier use and enforcement reports into the project's database:

* Visit California's State Water Resources Control Board [Water Conservation Portal](http://www.waterboards.ca.gov/water_issues/programs/conservation_portal/conservation_reporting.shtml) and find the "Current Reporting Data." Specifically we're looking for a link to an Excel file usually titled "Urban Water Supplier Report Dataset."

* Open ```development.yml``` and add data settings beginning on line 29

    * ```file_download_path``` is the absolute path to where we will download the Excel file so we can process and retrieve monthly use and monthly enforcement data

            file_download_path: "/Users/ckeller/_programming/2kpcc/django_projects/cali_water_reports/monthly_water_reports"

    * ```data_path``` is the absolute path to the ```data``` directory in the project's ```monthly_water_reports``` directory. This is where we store the files for archiving purposes after processing. For example

            data_path: "/Users/ckeller/_programming/2kpcc/_projects/cali_water_reports/monthly_water_reports/data"

    * ```enforcement_file``` is the link to the Urban Water Supplier Report Enforcement Excel file. This used to be housed in a seprate Excel file. Now it's included in the main file. For now we'll just enter the link twice.

            enforcement_file: "http://www.waterboards.ca.gov/water_issues/programs/conservation_portal/docs/2017feb/uw_supplier_data020817.xlsx"

    * ```usage_file``` is the link to the Urban Water Supplier Report Dataset Excel file. This used to be housed in a seprate Excel file. Now it's included in the main file. For now we'll just enter the link twice.

            usage_file: "http://www.waterboards.ca.gov/water_issues/programs/conservation_portal/docs/2017feb/uw_supplier_data020817.xlsx"

* Run the tests to gauge whether the Excel files can be downloaded and converted to csv files, and whether the required use and enforcement keys can be found, which are needed to ingest data into the database.

        fab test
        [localhost] local: python manage.py test
        Creating test database for alias 'default'...
        DEBUG: test_fetch_methods.py (def test_a_download_chain 164):  Processing usage
        DEBUG: test_fetch_methods.py (def Test_can_get_response_success_from_url 183):  test if able to download report from url
        DEBUG: test_fetch_methods.py (def Test_can_write_excel_file_from 193):  test can I write an excel file from url
        DEBUG: test_fetch_methods.py (def Test_can_convert_excel_file_to 207):  can I make an excel file out of this
        DEBUG: test_fetch_methods.py (def Test_can_find_expected_keys 221):  are the keys I expect to be in the file present
        DEBUG: test_fetch_methods.py (def Test_can_make_string_to_datetime 232):  can i make a string into a datetime object
        DEBUG: test_fetch_methods.py (def test_a_download_chain 164):  Processing enforcement
        DEBUG: test_fetch_methods.py (def Test_can_get_response_success_from_url 183):  test if able to download report from url
        DEBUG: test_fetch_methods.py (def Test_can_write_excel_file_from 193):  test can I write an excel file from url
        DEBUG: test_fetch_methods.py (def Test_can_convert_excel_file_to 207):  can I make an excel file out of this
        DEBUG: test_fetch_methods.py (def Test_can_find_expected_keys 221):  are the keys I expect to be in the file present
        DEBUG: test_fetch_methods.py (def Test_can_make_string_to_datetime 232):  can i make a string into a datetime object

* Use the Fabric command to fetch the latest batch of enforcement stats.

        fab fetch_enforcement_stats

* Use the Fabric command to fetch the latest batch of usage stats.

        fab fetch_water_use

* If everything processed approrpriately you should now be able to run the development server with ```fab run``` and view the site to do spot checks at [http://127.0.0.1:8000/](http://127.0.0.1:8000/)

    * Pages I would spot check monthly water use and average daily water consumption include:
        * [http://127.0.0.1:8000/monthly-water-use/region/south-coast/](http://127.0.0.1:8000/monthly-water-use/region/south-coast/)
        * [http://127.0.0.1:8000/monthly-water-use/city-of-pasadena/](http://127.0.0.1:8000/monthly-water-use/city-of-pasadena/)
        * [http://127.0.0.1:8000/monthly-water-use/city-of-burbank/](http://127.0.0.1:8000/monthly-water-use/city-of-burbank/)
        * [http://127.0.0.1:8000/monthly-water-use/city-of-glendale/](http://127.0.0.1:8000/monthly-water-use/city-of-glendale/)
        * [http://127.0.0.1:8000/monthly-water-use/region/south-coast/enforcement-comparison/](http://127.0.0.1:8000/monthly-water-use/region/south-coast/enforcement-comparison/)

How We Build The Project Each Month
===================================

This step comes after we have processed and ingested the newest data from California's [State Water Resources Control Board](http://www.waterboards.ca.gov/).

We use [django-bakery](https://django-bakery.readthedocs.io/en/latest/) to build out the ["Is California water use increasing?"](http://projects.scpr.org/applications/monthly-water-use/) news application to a series of static HTML pages.

* Build parameters can be found in ```development.yml```.

    * ```staging```: A boolean value that adjust some URLs during the baking process. Default value is ```False```. Set to ```True``` before baking out the pages so you can view baked pages on a local development server prior to deploying. Set to ```False``` prior to baking out the pages and deploying to the server.

    * ```staging_prefix```: A string value that is the prefix to where you can access your local development server. For instance if you start your local development server from within the static-projects repo using ```python -m SimpleHTTPServer 8880``` this value would be ```http://127.0.0.1:8880/```.

    * ```live_prefix```: For our purposes this value will always be ```http://projects.scpr.org```.

    * ```deploy_dir```: For our purposes this value will always be the location of the project in the static-projects repo which is ```/applications/monthly-water-use```.

    * ```build_dir``` Absolute path to the location on your machine to the static-projects repository. Might be something like ```"/Users/ckeller/_programming/2kpcc/_projects/static_projects/applications/monthly-water-use"```.

    * ```views``` are the django views that represent the pages we want to build out. The views we currently have are:

        - monthly_water_reports.views.InitialIndex
            - Example in the wild: http://projects.scpr.org/applications/monthly-water-use/
            - The code: https://github.com/SCPR/cali_water_reports/blob/master/monthly_water_reports/views.py#L27

        - monthly_water_reports.views.RegionDetailView
            - Example in the wild: http://projects.scpr.org/applications/monthly-water-use/region/south-coast
            - The code: https://github.com/SCPR/cali_water_reports/blob/master/monthly_water_reports/views.py#L127

        - monthly_water_reports.views.RegionEmbedView
            - Example in the wild: http://projects.scpr.org/applications/monthly-water-use/share/south-coast/
            - The code: https://github.com/SCPR/cali_water_reports/blob/master/monthly_water_reports/views.py#L285

        - monthly_water_reports.views.ComparisonIndex
            - Example in the wild: http://projects.scpr.org/applications/monthly-water-use/region/south-coast/reduction-comparison/
            - The code: https://github.com/SCPR/cali_water_reports/blob/master/monthly_water_reports/views.py#L409

        - monthly_water_reports.views.EnforcementIndex
            - Example in the wild: http://projects.scpr.org/applications/monthly-water-use/region/south-coast/enforcement-comparison/
            - The code: https://github.com/SCPR/cali_water_reports/blob/master/monthly_water_reports/views.py#L481

        - monthly_water_reports.views.SupplierDetailView
            - Example in the wild: http://projects.scpr.org/applications/monthly-water-use/city-of-compton/
            - The code: https://github.com/SCPR/cali_water_reports/blob/master/monthly_water_reports/views.py#L547

* When you are ready to build the project

    * Change into the project directory

            cd cali_water_reports

    * Open ```development.yml``` and set the ```staging``` value on line 36 to ```True```

    * Run ```fab build``` to start baking the pages

    * To preview the build, in a new terminal window change into wherever your KPCC work is and start your local development server

            python -m SimpleHTTPServer 8880

    * Spot check the *"baked"* or static HTML pages you have created:

        * [http://127.0.0.1:8880/monthly-water-use/region/south-coast/](http://127.0.0.1:8000/monthly-water-use/region/south-coast/)

        * [http://127.0.0.1:8880/monthly-water-use/city-of-pasadena/](http://127.0.0.1:8000/monthly-water-use/city-of-pasadena/)

        * [http://127.0.0.1:8880/monthly-water-use/city-of-burbank/](http://127.0.0.1:8000/monthly-water-use/city-of-burbank/)

        * [http://127.0.0.1:8880/monthly-water-use/city-of-glendale/](http://127.0.0.1:8000/monthly-water-use/city-of-glendale/)

        * [http://127.0.0.1:8880/monthly-water-use/region/south-coast/enforcement-comparison/](http://127.0.0.1:8000/monthly-water-use/region/south-coast/enforcement-comparison/)

    * If everything looks OK, let's build for real.

    * Open ```development.yml``` and set the ```staging``` value on line 36 to ```Falses```

    * Run ```fab build``` to start baking the pages

How We Deploy The Project Each Month
====================================

* Assuming you want to deploy this to the ```static-projects``` server, at this point you can build *"baked"* or static HTML version of the application.

    * Open a new terminal window and change into ```static-projects```

            cd static-projects

    * Make sure the master branch is up-to-date

            git pull

    * Switch to your development branch

            git checkout aaron-dev

    * Make sure your development branch is current with the master branch

            git merge aaron-dev master

    * *If you do git status and see a bunch of modified files that’s good.*

    * *If you see blue files, that means something new was created - most likely a water supplier that hadn't existed before - and you'll probably want to explore why.*

    * In the ```static-projects``` repo, commit and push your changes

            git commit -a -m "updates with a new build of the monthly water use application"
            git push

    * [Submit a pull request](https://github.com/SCPR/static-projects/pulls)

    * You can now use deploybot in Slack to send your updated code to the server for the world to see

Available Fabric Commands
=========================

**Data Processing and Update Functions**

* ```fab test```: run the cali_water application tests before attempting to update with new data

        local("python manage.py test")

* ```fetch_enforcement_stats```: pull down the Excel file with the monthly enforcement stats, convert to csv and ingest into database.

        local("python manage.py fetch_enforcement_stats")

* ```fetch_water_use```: pull down the Excel file with the monthly usage stats, convert to csv and ingest into database.

        local("python manage.py fetch_usage_stats")


**Development Functions**

* ```run```: shortcut for base manage.py function to launch the Django development server

        local("python manage.py runserver")

* ```make```: shortcut for base manage.py function to make Django database migrations to sync the dev database

        local("python manage.py makemigrations")

* ```migrate```: shortcut for base manage.py function to apply Django database migrations

        local("python manage.py migrate")

* ```superuser```: shortcut for base manage.py function to create a superuser

        local("python manage.py createsuperuser")


**Data Export Functions**

* ```dump_regions```: shortcut to dump hydrologic region data fixtures

        local("python manage.py dumpdata monthly_water_reports.hydrologicregion > monthly_water_reports/fixtures/hydrologic_regions.json")


* ```dump_suppliers```: shortcut to dump water supplier data fixtures

        local("python manage.py dumpdata monthly_water_reports.watersupplier > monthly_water_reports/fixtures/water_suppliers.json")


* ```dump_reports```: shortcut to dump monthly water supplier use reports data fixtures

        local("python manage.py dumpdata monthly_water_reports.watersuppliermonthlyreport > monthly_water_reports/fixtures/supplier_reports.json")


* ```dump_enforcement```: shortcut to dump monthly water supplier enforcement statistics data fixtures

        local("python manage.py dumpdata monthly_water_reports.waterenforcementmonthlyreport > monthly_water_reports/fixtures/enforcement_reports.json")


* ```dump_conservation```: shortcut to dump water conservation data fixtures

        local("python manage.py dumpdata monthly_water_reports.waterconservationmethod > monthly_water_reports/fixtures/conservation_methods.json")


* ```dump_fixtures```: shortcut to dump all data fixtures with logging

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


**Data Import Functions**

* ```load_regions```: shortcut to load hydrologic region data fixtures

        local("python manage.py loaddata monthly_water_reports/fixtures/hydrologic_regions.json")


* ```load_suppliers```: shortcut to load water supplier data fixtures

        local("python manage.py loaddata monthly_water_reports/fixtures/water_suppliers.json")


* ```load_reports```: shortcut to load monthly water supplier use reports data fixtures

        local("python manage.py loaddata monthly_water_reports/fixtures/supplier_reports.json")


* ```load_enforcement```: shortcut to load monthly water supplier enforcement statistics data fixtures

        local("python manage.py loaddata monthly_water_reports/fixtures/enforcement_reports.json")


* ```load_conservation```: shortcut to load water conservation data fixtures

        local("python manage.py loaddata monthly_water_reports/fixtures/conservation_methods.json")


* ```load_fixtures```: shortcut to load all data fixtures with logging

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


**Bootstrapping Functions**

* ```rename_files ```: shortcut to install requirements from repository's requirements.txt
        os.rename("cali_water_reports/settings_common.py.template", "cali_water_reports/settings_common.py")
        os.rename("cali_water_reports/settings_production.py.template", "cali_water_reports/settings_production.py")


* ```requirements```:  shortcut to install requirements from repository's ```requirements.txt```

        local("pip install -r requirements.txt")


* ```create_db```: Creates a database based on DATABASE variables in ```settings_development.py``` file

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


* ```makesecret```: generates secret key for use in [django settings](https://github.com/datadesk/django-project-template/blob/master/fabfile/makesecret.py)

        key = ''.join(random.choice(allowed_chars) for i in range(length))
        print 'SECRET_KEY = "%s"' % key


* ```build```: Activates the django-bakery script to build the views specified in ```settings_development.py```

        local("python manage.py build")


* ```buildserver```: Activates the django-bakery development server

        local("python manage.py buildserver")


* ```bootstrap```: Attempts to scaffold the project by:
        * Creating the database
        * Applying initial Django migrations
        * Ingesting the initial data fixtures
        * Creating the Django superuser
        * Running the Django development server

Mac OS Python development environment
=====================================

* Assumming homebrew is installed...

    * Install homebrew python

            cd /System/Library/Frameworks/Python.framework/Versions
            sudo rm Current
            brew install python
            brew doctor
            which python
            which pip
            pip install --upgrade setuptools
            pip install --upgrade distribute
            pip install virtualenv
            pip install virtualenvwrapper
            python --version
            source /usr/local/bin/virtualenvwrapper.sh
            sudo ln -s /usr/local/Cellar/python/2.7.8_2 /System/Library/Frameworks/Python.framework/Versions/Current

    * Configure $PATH variables for python, virtualenv

            # homebrew path
            export PATH="/usr/local/bin:$PATH"

            # virtualenvwrapper settings
            export WORKON_HOME=$HOME/.virtualenvs
            export PIP_VIRTUALENV_BASE=$WORKON_HOME
            export PIP_RESPECT_VIRTUALENV=true
            source /usr/local/bin/virtualenvwrapper.sh

    * Install MySQL via homebrew

            brew remove mysql
            brew cleanup
            launchctl unload -w ~/Library/LaunchAgents/homebrew.mxcl.mysql.plist
            rm ~/Library/LaunchAgents/homebrew.mxcl.mysql.plist
            sudo rm -rf /usr/local/var/mysql
            brew install mysql
            ln -sfv /usr/local/opt/mysql/*.plist ~/Library/LaunchAgents

    * Getting mysql up and running

            mysql.server start
            mysql_secure_installation
            mysql -u root -p
            SHOW DATABASES;
            SET default_storage_engine=MYISAM;
