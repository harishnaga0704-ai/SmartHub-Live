"""Project configuration package.

mysqlclient is installed in this project, so Django can use its native
``MySQLdb`` driver directly.  Keeping this file free of a PyMySQL import also
allows management commands to start when PyMySQL is not installed.
"""
