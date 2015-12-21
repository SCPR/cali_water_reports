Processing Monthly California Water Reports
===========================================

This django project/application processes the monthly water reports from the [State Water Resources Control Board](http://www.waterboards.ca.gov/waterrights/water_issues/programs/drought/docs/ws_tools/guidance_estimate_res_gpcd.pdf) and builds KPCC's news application ["Where is California water use decreasing?"](http://projects.scpr.org/applications/monthly-water-use/)

Table of Contents
=================

* [Quickstart](#quickstart)
* [Monthly Process To Update Data and Build the Project](#monthly-process-to-update-data-and-build-the-project)
* [Available Fabric Commands](#available-fabric-commands)
* [Building a Mac OS Python dev environment](#building-a-mac-os-python-dev-environment)

Quickstart
==========

* Clone this repo to wherever it is on your machine that you work on your projects

        git clone git@github.com:chrislkeller/cali_water_reports.git

* Change into that directory

        cd cali_water_reports

* Rename ```TEMPLATE_development.yml``` to ```development.yml```

* Run ```fab makesecret``` and add the output on line 5 of ```development.yml```

* Assuming you have MySQL installed, open ```development.yml``` and add ```cali_water_reports``` as the database name on line 17. Add in any username and password you might have for your MySQL install.

        database:
          host: "127.0.0.1"
          port: 3306
          database: "project_name"
          username: "root"
          password: ""

* Assuming you have virtualenv and pip installed run ```fab bootstrap```

    * This attempts to scaffold the project by:
        * Creating virtualenv
        * Activating the virtualenv
        * Installing requirements
        * Creating the database
        * Applyin initial Django migrations
        * Creating the Django superuser
        * Running the Django development server

* Activate your virtualenv which should be named ```cali_water_reports```

        workon cali_water_reports

* Open ```development.yml``` and add data settings beginning on line 37

    * ```data_path``` is ...

            data_path = /Users/ckeller/_programming/2kpcc/django_projects/cali_water_reports/monthly_water_reports/data

    * ```file_download_path``` is ...

            file_download_path = /Users/ckeller/_programming/2kpcc/django_projects/cali_water_reports/monthly_water_reports

    * For the most part, use the following build parms ...

            build:
              bakery_gzip: False
              staging: False
              staging_prefix: "http://127.0.0.1:8880/2kpcc/static-projects"
              live_prefix: "http://projects.scpr.org"
              deploy_dir: "/applications/monthly-water-use"
              build_dir: "/Users/ckeller/_programming/2kpcc/static-projects/applications/monthly-water-use"
              views:
                - "monthly_water_reports.views.InitialIndex"
                - "monthly_water_reports.views.RegionDetailView"
                - "monthly_water_reports.views.RegionEmbedView"
                - "monthly_water_reports.views.ComparisonIndex"
                - "monthly_water_reports.views.EnforcementIndex"
                - "monthly_water_reports.views.SupplierDetailView"

    * At this point you should be able to run ```fab run``` and navigate [http://127.0.0.1:8000/monthly-water-use](http://127.0.0.1:8000/monthly-water-use) and see a Django error page because there is no data in the database, which takes us to...

----

Monthly Process To Update Data and Build the Project
====================================================

* Change into that directory

        cd cali_water_reports

* Activate the virtual environment
    * Assuming you use the virtual environment created during the bootstrap process

            workon cali_water_reports

* Open ```development.yml``` and:

    *  change two URLs which are paths to the two data files provided by the [State Water Resources Control Board](http://www.waterboards.ca.gov/water_issues/programs/conservation_portal/conservation_reporting.shtml)

        * ```enforcement_file``` is the link to the Urban Water Supplier Enforcement Statistics Excel file

                enforcement_file: "http://www.waterboards.ca.gov/water_issues/programs/conservation_portal/docs/2015dec/120115_enforcement_statistics.xlsx"

        * ```usage_file``` is the link to the monthly Urban Water Supplier Report Excel file

                usage_file: "http://www.waterboards.ca.gov/water_issues/programs/conservation_portal/docs/2015dec/uw_supplier_data120115.xlsx"

        * Set ```staging``` to ```True```

        * Make sure the views you want to build are valid and are not commented out

                views:
                  - "monthly_water_reports.views.InitialIndex"
                  - "monthly_water_reports.views.RegionDetailView"
                  - "monthly_water_reports.views.RegionEmbedView"
                  - "monthly_water_reports.views.ComparisonIndex"
                  - "monthly_water_reports.views.EnforcementIndex"
                  - "monthly_water_reports.views.SupplierDetailView"

* Run the tests to gauge whether the Excel files can be downloaded, converted to csv files and ingested into the database.

        fab test

* Use the Fabric command to fetch the latest batch of enforcement stats.

        fab fetch_enforcement_stats


* Use the Fabric command to fetch the latest batch of usage stats.

        fab fetch_water_use

* If everything processed approrpriately you should now be able to view the site and do spot checks at [http://127.0.0.1:8000/monthly-water-use](http://127.0.0.1:8000/monthly-water-use)

        fab run

    * Pages I would spot check include:
        * [http://127.0.0.1:8000/monthly-water-use/region/south-coast/](http://127.0.0.1:8000/monthly-water-use/region/south-coast/)
        * [http://127.0.0.1:8000/monthly-water-use/city-of-pasadena/](http://127.0.0.1:8000/monthly-water-use/city-of-pasadena/)
        * [http://127.0.0.1:8000/monthly-water-use/city-of-burbank/](http://127.0.0.1:8000/monthly-water-use/city-of-burbank/)
        * [http://127.0.0.1:8000/monthly-water-use/city-of-glendale/](http://127.0.0.1:8000/monthly-water-use/city-of-glendale/)
        * [http://127.0.0.1:8000/monthly-water-use/region/south-coast/enforcement-comparison/](http://127.0.0.1:8000/monthly-water-use/region/south-coast/enforcement-comparison/)

* Assuming you want to deploy this to the ```static-projects``` server, at this point you can build *"baked"* or static HTML version of the application.

    * Open a new terminal window and change into ```static-projects```

            cd static-projects

    * Make sure the master branch is up-to-date

            git pull

    * Switch to your development branch

            git checkout aaron-dev

    * Make sure your development branch is current with the master branch

            git merge aaron-dev master

    * Build the application

            fab build

        * *If you do git status and see a bunch of modified files that’s good.*
        * *If you see blue files, that means something new was created - most likely a water supplier that hadn't existed before - and you'll probably want to explore why.*

    * Open a new terminal window and start your development server

            python -m SimpleHTTPServer 8880

    * Spot check the *"baked"* or static HTML pages you have created:
        * [http://127.0.0.1:8880/monthly-water-use/region/south-coast/](http://127.0.0.1:8000/monthly-water-use/region/south-coast/)
        * [http://127.0.0.1:8880/monthly-water-use/city-of-pasadena/](http://127.0.0.1:8000/monthly-water-use/city-of-pasadena/)
        * [http://127.0.0.1:8880/monthly-water-use/city-of-burbank/](http://127.0.0.1:8000/monthly-water-use/city-of-burbank/)
        * [http://127.0.0.1:8880/monthly-water-use/city-of-glendale/](http://127.0.0.1:8000/monthly-water-use/city-of-glendale/)
        * [http://127.0.0.1:8880/monthly-water-use/region/south-coast/enforcement-comparison/](http://127.0.0.1:8000/monthly-water-use/region/south-coast/enforcement-comparison/)

    * If everything looks OK, let's build for real.

    * Open ```development.yml``` and set ```staging``` to ```False```

    * Build the application

            fab build

    * In the ```static-projects``` repo, commit and push your changes

            git commit -a -m "updates with a new build of the monthly water use application"
            git push

    * [Submit a pull request](https://github.com/SCPR/static-projects/pulls)

    * You can now use deploybot to send your updated code to the server for the world to see

----

Available Fabric Commands
=========================

**Data Functions**

* ```fab test```: run the cali_water application tests

        local("python manage.py test")

* ```fetch_enforcement_stats```: pull down the excel file with the monthly enforcement stats, convert to csv and ingest into database.

        local("python manage.py fetch_enforcement_stats")

* ```fetch_water_use```: pull down the excel file with the monthly usage stats, convert to csv and ingest into database.

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

**Bootstrapping Functions**

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

* ```move```

        local("python manage.py move_baked_files")

* ```bootstrap```: Attempts to scaffold the project by:
        * Creating virtualenv
        * Activating  the virtualenv
        * Installing requirements
        * Creating the database
        * Applying initial Django migrations
        * Creating the Django superuser
        * Running the Django development server

            with prefix("WORKON_HOME=$HOME/.virtualenvs"):
                with prefix("source /usr/local/bin/virtualenvwrapper.sh"):
                    local("mkvirtualenv %s" % (env.project_name))
                    with prefix("workon %s" % (env.project_name)):
                        requirements()
                        time.sleep(2)
                        create_db()
                        time.sleep(2)
                        migrate()
                        time.sleep(2)
                        local("python manage.py createsuperuser")
                        run()

----

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
