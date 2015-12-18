

### cali_water_reports

#### Quickstart

**To bootstrap the project**:

* This assumes you have Django 1.7 and Fabric installed outside of your virtualenv(s).

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

**Documentation**:

* Developer documentation is available in Sphinx format in the docs directory.
* Initial installation instructions (including how to build the documentation as
HTML) can be found in docs/install.rst.
