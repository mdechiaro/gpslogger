#!/usr/bin/python
"""
Simple Web Class that accepts output from the Android GPSLogger app.

The app should be configured to use "Log to custom URL."
"""
import cherrypy
from cherrypy.process.plugins import Daemonizer
import os
from ConfigParser import SafeConfigParser
# pylint: disable=relative-import
from dbgps import DBGPS


# pylint: disable=too-few-public-methods
class API(DBGPS):
    """
    Accepts information from Android app GPSLogger.
    """
    def __init__(self):
        self.config = {
            'global': {
                'server.socket_host': '0.0.0.0',
                'server.socket_port': 8080,
            },
        }

        # override options with defaults in dotfiles
        dotrc_parser = SafeConfigParser()
        dotrc_name = '~/.gpsloggerrc'
        dotrc_path = os.path.expanduser(dotrc_name)
        dotrc_parser.read(dotrc_path)
        #
        user = dotrc_parser.get('mysql', 'user')
        passwd = dotrc_parser.get('mysql', 'passwd')
        host = dotrc_parser.get('mysql', 'host')
        db_name = dotrc_parser.get('mysql', 'db_name')
        # id of android device
        self.aid = dotrc_parser.get('android', 'aid')
        #
        DBGPS.__init__(self, host, user, passwd, db_name)

    # pylint: disable=no-self-use
    @cherrypy.expose
    def gps(self, **kwargs):
        """
        This is a subfolder called "gps" for cherrypy.  The app is currently
        configured to send the data to the following:

        http://www.hostname.com/gps?

        All information is passed to it as a dictionary after the "?" from
        GPSLogger, and can be passed to a database or other application.
        """
        # add the ipaddr to dictionary
        kwargs.update({'ipaddr':cherrypy.request.headers['Remote-Addr']})

        # ensure column is filled with NULL for blank values
        for key, value in kwargs.iteritems():
            if not value:
                kwargs[key] = 'NULL'

        # cheap security, only insert values if android id matches.
        if kwargs['aid'] == self.aid:
            self.insert('data', **kwargs)


if __name__ == '__main__':
    # pylint: disable=invalid-name
    gps_api = API()
    Daemonizer(cherrypy.engine).subscribe()
    cherrypy.quickstart(gps_api, '/', gps_api.config)
