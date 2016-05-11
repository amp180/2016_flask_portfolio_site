"""
Routes and views for the flask application.
"""

from multiprocessing import Pool
import datetime
import json
from flask import render_template, request, flash
from flask import make_response, redirect, url_for, jsonify
from __init__ import app
import db_models
from util_functions import *

from room_checker import dcu_lab_free_now, get_dcu_calendar_code, dcu_open_now, FREE, BOOKED, CLOSED, TIMETABLE_NOT_AVAILABLE

@app.route('/')
def home(*args, **kwargs):
    """Renders the home page."""
    return render_template(
        'index.html',
        title='Home ',
        year = datetime.date.today().year,
        age = age(),
    )


@app.route("/cv")
@app.route("/CV")
def cv():
    """Renders my CV."""
    return render_template(
        "cv.html",
        title = "CV",
        year = datetime.date.today().year,
        age = age(),
    )

@app.route('/projects')
@app.route('/Projects')
def projects(*args,**kwargs):
    """Displays full list of projects."""
    query = db_models.Project.query.all()
    return render_template(
            'project_list.html',
            title = 'Projects',
            year = datetime.date.today().year,
            age = age(),
            projects = query,
            enumerate=enumerate 
        )

@app.route('/projects/<slug>')
@app.route('/Projects/<slug>')
def project(slug, *args,**kwargs):
    """Displays a project given it's database id."""
    return render_template(
            'project.html',
            title = 'Project %s  ' % slug,
            year = datetime.date.today().year,
            age = age(),
            proj =  db_models.Project.query.get(int(slug))
        )

@app.route('/ip')
@app.route('/IP')
def ip(*args, **kwargs):
    """Returns the client their IP address."""
    flash(request.remote_addr)

    if request.referrer and (request.referrer.lower().find('pegman.space') != -1):
        return redirect(request.referrer) #go back to the page we came from if possible

    return redirect(url_for('home')) 

@app.route('/DCU_Rooms')
@app.route('/dcu_rooms')
def dcu_rooms(*args, **kwargs):
    """Returns the status of labs in DCU."""
    rooms = ['GLA.LG25', 'GLA.LG26', 'GLA.L114', 'GLA.L101', 'GLA.L128', 'GLA.L125', 'GLA.C204', 'GLA.C206', 'GLA.C214']
    #use thread pool to look up availability
    availability = Pool(9).map(dcu_lab_free_now, rooms)

    if not dcu_open_now():
        flash("DCU isn't normally open at this time."); 
    if all( a is BOOKED for a in availability ):
        flash("All labs are booked for the current slot.")
    if TIMETABLE_NOT_AVAILABLE in availability:
           flash("Failed to get timetable for one or more labs.");
    
    calendar_code = get_dcu_calendar_code()
    
    return render_template( 'dcu_rooms.html',  
                           year = datetime.date.today().year,
                           title='DCU Lab Bookings',
                           room_availability=zip(rooms, availability),
                           FREE=FREE, 
                           BOOKED=BOOKED,
                           week=calendar_code['week'],
                           day=calendar_code['day'],
                           hour=calendar_code['hour'],
                           )

@app.route('/fatty/', methods=['POST', 'GET'])
@app.route('/fatty/submit', methods=['POST', 'GET'])
def fatty(*args, **kwargs):
    """Serve Fatty Form Page, render fatty meme images."""
    if 'caption1' in request.values or 'caption2' in request.values:
               res = make_response( 
                        meme( 
                                request.values['caption1'], 
                                request.values['caption2'] 
                           ).read() 
                        )
               res.headers['Content-type'] = 'image/jpeg'
               return res
    else:
        return render_template(
                 'fatty.html', 
                 title = "Fatty ",
                 year=datetime.date.today().year 
               )

@app.route('/fatty/<cap1>/<cap2>', methods=['POST', 'GET'])
@app.route('/fatty/<cap1>/<cap2>/', methods=['POST', 'GET'])
@app.route('/fatty/<cap1>/<cap2>/<fname>', methods=['POST', 'GET'])
def fatty_plain_url(cap1, cap2, fname="fatty.jpg", *args, **kwargs):
    """
        Cleaner url for fatty images, since it's free of ?&; chars,
        you can post it in minecraft chats and other places with sensitive formatting.
    """
    return redirect( 
                url_for('fatty') 
                + "?caption1=%s&caption2=%s&/%s" % (cap1, cap2, fname) 
            )

