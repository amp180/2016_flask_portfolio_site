#!/usr/bin/env python2.6
#import libraries
from flask import flash
import datetime
import pytz
from lxml import html
import requests
import requests_cache


#cache the requests library for 35 minutes.
#this is needed so if anyone actually uses the lab checker it won't be hammering dcu's timetable server.
#Can't cache longer as it's only requesting 1*1 timetables for easier parsing, code to handle column span would be kinda ugly.
requests_cache.install_cache(expire_after=(60*60*35), backend='sqlite') 

#Constants
IRISH_TIME = pytz.timezone('Europe/Dublin')

#Return value constants
FREE = "Free"
BOOKED = "Booked"
CLOSED = "Closed"
TIMETABLE_NOT_AVAILABLE = "Timetable not avalable"


def dcu_lab_timetable(room="GLA.LG25", week="20", hour="1", day="1"):
    """Finds out if a room in DCU is free at the given week/day/hour number."""
    #Queries dcu timetable app. Weeks seem to start from sept21, hours are from 8am in 30 min incs, day 1 is monday.
    #Create url for a 1x1 timetable
    url = "http://www101.dcu.ie/timetables/feed.php?room={0}&week1={1}&hour={2}&day={3}&template=location".format(room, week, hour, day)
    page = requests.get(url)
    tree = html.fromstring(page.content)
    table_entry = tree.xpath("/html/body/table[2]/tr[2]/td[2]") #Get list containing table cell.

    if not table_entry: #If there was no table on the page.
       return TIMETABLE_NOT_AVAILABLE
    elif table_entry[0].xpath("""img""") != []: #Detect the blank image in empty cells.
       return FREE
    else:
       return BOOKED


def current_irish_time():
     #Get current time, uses utc and then translates to Irish time to match DCU.
     #Nescessary if local time isn't irish time,
     #as is case on my shared hosting, which doesn't switch for daylight savings.
     now_utc = datetime.datetime.utcnow().replace(tzinfo=pytz.utc)
     return now_utc.astimezone(IRISH_TIME)


def dcu_open_now(now=None):
    """Returns whether the DCU SOC is normally open on a given datetime."""
    if now is None:
       now = current_irish_time()

    #Get some times earlier/later today.
    _8am = now.replace(hour=8, minute=0)
    _6pm = now.replace(hour=18, minute=0)
    _10pm = now.replace(hour=22, minute=0)
    is_weekend = now.weekday() >= 5

    #opening hours for dcu soc are 8am-10pm or 6pm weekends during the semester.
    return now > _8am and now < _10pm and not (now > _6pm and is_weekend)


def semester_one_date(year):
     """returns monday of 3rd week of september in a given year."""
     _21st_sept = datetime.datetime(day=21, month=9, year=year, tzinfo=IRISH_TIME)
     return _21st_sept - datetime.timedelta(days=_21st_sept.weekday()-1)


def get_dcu_calendar_code(now=None):
    """Translate a datetime to a dcu week/day/hour number."""
    if now is None:
       now = current_irish_time()

    #get the year the current academic year started in
    is_before_first_semester = now < semester_one_date(now.year)
    academic_year = now.year-1 if is_before_first_semester else now.year

    #find number of weeks since first monday of academic year.
    sem1date = semester_one_date(academic_year)
    this_monday = now - datetime.timedelta(days=now.weekday()-1)
    
    #calculate week day and hour numbers for api
    week = int( (this_monday - sem1date).days / 7 ) +1 #weeks since week sept 21, 1 indexed
    day = now.weekday() + 1 #day of week (1 indexed)
    hour = int( (now.hour * 2) + (now.minute / 30) ) - 15 #half-hours since 8am, 1 indexed
    return dict(week=week, hour=hour, day=day)


def dcu_lab_free_now(room="GLA.LG25", now=None):
    """Finds out if a room is currently free. Takes a room code and optional datetime in the europe/dublin timezone."""
    if now is None:
       now = current_irish_time()

    if not dcu_open_now(now=now):
        return CLOSED 

    return dcu_lab_timetable(room=room, **get_dcu_calendar_code(now=now) )

