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

This directory houses a Flask application. Test the app locally with the following commands. It's necessary to set the host to `0.0.0.0` if the app is to be run in a virtual machine, or else requests from the host machine will be unable to reach the app.

```
export FLASK_APP=app.py
export FLASK_DEBUG=1
flask run --host=0.0.0.0
```
