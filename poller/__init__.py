"""
Startup code
"""

import os
import json
import logging
import requests
import datetime
import threading
from flask import Flask
from bs4 import BeautifulSoup
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate


POOL_TIME = 5 * 60 # Seconds
DASHBOARD_URL = 'https://rit.edu/ready/summer-dashboard'
DATA_THREAD = threading.Thread()

APP = Flask(__name__)

# Load default configuration and any environment variable overrides
_root_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
APP.config.from_pyfile(os.path.join(_root_dir, 'config.env.py'))

# Load file based configuration overrides if present
_pyfile_config = os.path.join(_root_dir, 'config.py')
if os.path.exists(_pyfile_config):
    APP.config.from_pyfile(_pyfile_config)

# Logger configuration
logging.getLogger().setLevel(APP.config['LOG_LEVEL'])
#pylint: disable=no-member
APP.logger.info('Launching rit-covid-poller v' + APP.config['VERSION'])

db = SQLAlchemy(APP)
migrate = Migrate(APP, db)
APP.logger.info('SQLAlchemy pointed at ' + repr(db.engine.url))
#pylint: enable=no-member

#pylint: disable=wrong-import-position
from . import models
from . import commands
from . import routes

db.create_all()

from .models import Day

def data_are_same(old, new):
    return old.total_students == new.total_students and \
        old.total_staff == new.total_staff and \
        old.new_students == new.new_students and \
        old.new_staff == new.new_staff and \
        old.quarantine_on_campus == new.quarantine_on_campus and \
        old.quarantine_off_campus == new.quarantine_off_campus and \
        old.isolation_on_campus == new.isolation_on_campus and \
        old.isolation_off_campus == new.isolation_off_campus and \
        old.beds_available == new.beds_available and \
        old.tests_administered == new.tests_administered and \
        old.alert_level == new.alert_level
            

def get_data():
    print('fetching data')
    global DATA_THREAD
    DATA_THREAD = threading.Timer(POOL_TIME, get_data, ())
    DATA_THREAD.start()
    page = requests.get(DASHBOARD_URL, headers={'Cache-Control': 'no-cache'})
    soup = BeautifulSoup(page.content, 'html.parser')
    #total_students = int(soup.find('div', attrs={'class': 'statistic-13872'}).find_all("p", attrs={'class': 'card-header'})[0].text.strip())
    #total_staff = int(soup.find('div', attrs={'class': 'statistic-13875'}).find_all("p", attrs={'class': 'card-header'})[0].text.strip())
    new_students = int(soup.find('div', attrs={'class': 'statistic-14884'}).find_all("p", attrs={'class': 'card-header'})[0].text.strip())
    new_staff = int(soup.find('div', attrs={'class': 'statistic-14887'}).find_all("p", attrs={'class': 'card-header'})[0].text.strip())
    #quarantine_on_campus = int(soup.find('div', attrs={'class': 'statistic-13893'}).find_all("p", attrs={'class': 'card-header'})[0].text.strip())
    #quarantine_off_campus = int(soup.find('div', attrs={'class': 'statistic-13896'}).find_all("p", attrs={'class': 'card-header'})[0].text.strip())
    #isolation_on_campus = int(soup.find('div', attrs={'class': 'statistic-13905'}).find_all("p", attrs={'class': 'card-header'})[0].text.strip())
    #isolation_off_campus = int(soup.find('div', attrs={'class': 'statistic-13908'}).find_all("p", attrs={'class': 'card-header'})[0].text.strip())
    #beds_available = int(soup.find('div', attrs={'class': 'statistic-13935'}).find_all("p", attrs={'class': 'card-header'})[0].text.strip().strip('%'))
    #tests_administered = int(soup.find('div', attrs={'class': 'statistic-13923'}).find_all("p", attrs={'class': 'card-header'})[0].text.strip().replace("*", " ").replace(",", ""))
    #container = soup.find('div', attrs={'id': 'pandemic-message-container'})
    #alert_level = container.find('a').text
    color = ""
    #if "Green" in alert_level:
    #    color = 'green'
    #elif "Yellow" in alert_level:
    #    color = 'yellow'
    #elif "Orange" in alert_level:
    #    color = 'orange'
    #elif "Red" in alert_level:
    #    color = 'red'

    #fall_data = None
    #with open('history/fall-2020.json', 'r') as fd:
    #    fall_data = json.loads(fd.read())
    current_data = Day(
        last_updated=datetime.datetime.now(),
        alert_level=color,
        beds_available=-1,
        isolation_off_campus=-1,
        isolation_on_campus=-1,
        new_staff=new_staff,
        new_students=new_students,
        quarantine_off_campus=-1,
        quarantine_on_campus=-1,
        tests_administered=-1,
        total_staff=-1,
        total_students=-1)
    print(current_data.serialize())
    try:
        if not data_are_same(Day.get_all()[-1], current_data):
            db.session.add(current_data)
    except IndexError:
            db.session.add(current_data)
    dedup()
    return current_data

def dedup():
    data = Day.get_all()
    # get first date
    starting_date = data[-1].serialize()['last_updated'].split(' ')[0]
    for i in range(len(data)-2, 0, -1):
        if data[i].serialize()['last_updated'].split(' ')[0] != starting_date:
            starting_date = data[i].serialize()['last_updated'].split(' ')[0]
        else:
            db.session.delete(data[i])
            print('dropped ' + data[i].serialize()['last_updated'])
    db.session.commit()

get_data()
