rdb-fullstack
=============

Common code for the Relational Databases and Full Stack Fundamentals courses


Project: Tournament Results
---------------------------

Code for this project can be found in `vagrant/tournament`.

Within that directory, tests can be run with `python tournament_test.py`.

Tests assume that a database and tables have already been constructed. To do this, execute the `tournament.sql` script.

```
$ psql -f tournament.sql
```


Project: Item Catalog
---------------------

Code for this project can be found in `vagrant/catalog`.

This directory houses a [Flask](http://flask.pocoo.org/) application. Test the app locally with the following commands. It's necessary to set the host to `0.0.0.0` if the app is to be run in a virtual machine, or else requests from the host machine will be unable to reach the app.

```
export FLASK_APP=app.py
export FLASK_DEBUG=1
flask run --host=0.0.0.0
```

Before running, the local database should be created by running `python database_setup.py`. The `populate_database.py` script will create some basic records in the database to give the application some minimal content.

This application relies upon [Google Sign-in for Websites](https://developers.google.com/identity/sign-in/web/) to handle its authentication. To properly run, a `client_secrets.json` file will be necessary, and should be placed in the root directory of the application. Detailed instructions for acquiring such a file can be found in the Google Sign-In documentation.

The following endpoints will return JSON data if an `Accept: application/json` header is used.

```
/
/category/<category_name>
/category/<category_name>/item/<item>
```

For example:

```
~ $ curl --header "Accept: application/json" http://localhost:5000/category/Games/item/Chess
{
  "category": 1,
  "description": null,
  "id": 1,
  "name": "Chess",
  "user": 1
}
```
