Django Project Template
=======================

~~~This Django Project Template provides some defaults for new KPCC Django projects. It is based on [django-layout](https://github.com/lincolnloop/django-layout).~~~

~~~To use this template, run the following command:~~~

~~~django-admin.py startproject --template=https://github.com/chrislkeller/django-layout/zipball/master --extension=py,yml,md,gitignore cali_water_reports~~~

Quickstart
==========

**To bootstrap the project**:

* This assumes you have a Mac OS Python development environment up and running, and Django 1.8 and Fabric installed outside of your virtualenv(s).

    * pip install Django==1.8.4 Fabric==1.9.1

* Change into the project directory

        cd cali_water_reports

        ~~~* Rename ```config.yml.template``` to ```config.yml``` and ```development.yml.template``` to ```development.yml```~~~

* Open ```development.yml``` and add the name of your project as the database name on line 17.

        database:
          host: "127.0.0.1"
          port: 3306
          database: "project_name"
          username: "root"
          password: ""

~~~* Run ```fab makesecret``` and add the ```secret key``` to line 5 in ```development.yml```~~~

* Run ```fab bootstrap```
    * This attempts to scaffold the project by:
        * Creating virtualenv
        * Activating the virtualenv
        * Installing requirements
        * Creating the database
        * Applyin initial Django migrations
        * Creating the Django superuser
        * Running the Django development server

**Available Fabric Commands**:

* ```fab run```
    * Launches the Django development server

* ```fab make```
    * Creates Django database migrations

* ```fab migrate```
    * Applies Django database migrations

* ```fab requirements```
    * Installs Python packages from requirements.txt file

* ```fab create_db```
    * Creates a database based on DATABASE variables in ```settings_development.py``` file

* ```fab bootstrap```
    * Attempts to scaffold the project by:
        * Create virtualenv
        * Activates the virtualenv
        * Installs requirements
        * Creates the database
        * Applies initial Django migrations
        * Creates the Django superuser
        * Runs the Django development server

* ```fab build```
    * Activates the django-bakery script to build the views specified in ```settings_development.py```

* ```fab buildserver```
    * Activates the django-bakery development server

* ```fab commit```
    * Commits and pushes to the version control repo


----


* add ```monthly_water_reports``` to installed apps in ```development.yml```

        installed_apps:
          - "django_admin_bootstrapped"
          - "monthly_water_reports"


* add ```monthly_water_reports``` urls to ```cali_water_reports/urls.py```

        url(r"^monthly-water-use/", include("monthly_water_reports.urls")),

* Migrate the database to add the application tables

        fab migrate

----


Mac OS Python development environment
=====================================

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
