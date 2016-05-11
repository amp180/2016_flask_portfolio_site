#!/usr/bin/env python
import os, sys

# Change working directory so relative paths (and template lookup) are ensured
os.chdir(os.path.dirname(os.path.abspath(__file__)))
# Add local directory to python path, just in case
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

#setup cgi/wsgi app
from __init__ import app

from wsgiref.handlers import CGIHandler
from werkzeug.contrib.fixers import CGIRootFix 

#hide the script name from urls
class ScriptNameStripper(object):
    #modified to work with my setup, originally from:
    #http://librelist.com/browser/flask/2011/7/22/url-for-problem-in-apache-+-fastcgi/#2bf3cfe2aa7dc9243c63c356e243baf3
    to_strip = '/FlaskPortfolioPort/index.cgi'
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
