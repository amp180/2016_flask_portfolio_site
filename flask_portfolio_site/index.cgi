#!/usr/bin/env python
import os, sys

#setup cgi/wsgi app
from flask_portfolio_site import app

from wsgiref.handlers import CGIHandler
from werkzeug.contrib.fixers import CGIRootFix

#hide the script name from urls when you use mod-rewrite to make / relative to this script.
class ScriptNameStripper(object):
    #modified to work with my setup, originally from:
    #http://librelist.com/browser/flask/2011/7/22/url-for-problem-in-apache-+-fastcgi/#2bf3cfe2aa7dc9243c63c356e243baf3
    to_strip = '/index.cgi'
    def __init__(self, app):
        self.app = app
    def __call__(self, environ, start_response):
        path_info = environ.get('PATH_INFO', '')

	if path_info.startswith(self.to_strip):
        	environ['PATH_INFO'] = path_info[len(self.to_strip):]
		environ['PATH_TRANSLATED'] = 'redirect:' + environ['PATH_INFO']
	environ['SCRIPT_NAME'] = '/'

        return self.app(environ, start_response)


CGIHandler().run(ScriptNameStripper(app))
