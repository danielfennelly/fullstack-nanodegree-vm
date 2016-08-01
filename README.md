rdb-fullstack
=============

Common code for the Relational Databases and Full Stack Fundamentals courses

Project: Tournament Results
---------------------------

Code for this project can be found in `vagrant/tournament`.

Within that directory, tests can be run with `python tournament_test.py`.

Tests assume that a database and tables have already been constructed. To do this, execute the following in the Postgres console:

```
CREATE DATABASE tournament;
\i tournament.sql;
```
