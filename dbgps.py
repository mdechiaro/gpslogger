#!/usr/bin/python
""" MySQL DB class for GPS Coordinates."""
import MySQLdb

class DBGPS(object):
    """
    Class for accepting GPS coordinates into a mysql DB
    """
    def __init__(self, host, user, passwd, db_name):
        self.host = host
        self.user = user
        self.passwd = passwd
        self.db_name = db_name
        # pylint: disable=invalid-name
        self.db = MySQLdb.connect(
            self.host, self.user, self.passwd, self.db_name
        )

        # This dictionary is how we want our table to be setup
        self.gps_table = {
            'ipaddr':'int unsigned',
            'aid': 'char(30)',
            'time' : 'timestamp',
            'latitude':'decimal(11,8)',
            'longitude':'decimal(11,8)',
            'altitude' : 'float(6,1)',
            'annotation': 'text',

        }

        self.cursor = self.db.cursor()


    def create_db(self, database):
        """
        Creates a database using a database name
        """
        sql = 'CREATE DATABASE IF NOT EXISTS %s' % (database)
        self.cursor.execute(sql)


    def create_table(self, table, **kwargs):
        """
        Creates a table using a table name and dictionary of columns:types
        """
        args = ', '.join(
            ['%s %s' % (key, value) for key, value in kwargs.iteritems()]
        )
        sql = 'CREATE TABLE IF NOT EXISTS %s (%s)' % (table, args)
        self.cursor.execute(sql)


    def insert(self, table, **kwargs):
        """Insert method for adding data into database."""
        try:
            columns = ', '.join(kwargs.keys())
            # placeholders will be a string of %s to match number of columns
            placeholders = ', '.join(['%s'] * len(kwargs))
            data = (
                'INSERT INTO %s (%s) VALUES (%s)' %
                (table, columns, placeholders)
            )

            self.cursor.execute(data, kwargs.values())
            self.db.commit()
        except MySQLdb.Error:
            self.db.rollback()
