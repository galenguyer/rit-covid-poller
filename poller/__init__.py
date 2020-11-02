""" A small flask Hello World """

import os
import threading
import sqlite3
import atexit
import datetime

from flask import Flask, jsonify
import requests
from bs4 import BeautifulSoup

POOL_TIME = 5 * 60 # Seconds
DASHBOARD_URL = 'https://rit.edu/ready/dashboard'
LATEST_DATA = None
data_thread = threading.Thread()
db_lock = threading.Lock()

if not os.path.exists('./data'):
    os.mkdir('./data')

def interrupt():
    global data_thread
    data_thread.cancel()

def create_tables():
    with db_lock:
        db_conn = sqlite3.connect('data/data.sqlite3')
        c = db_conn.cursor()
        sql = f'CREATE TABLE IF NOT EXISTS `alertlevel` (time DATETIME PRIMARY KEY NOT NULL, color CHAR(50) NOT NULL);'
        c.execute(sql)
        sql = f'CREATE TABLE IF NOT EXISTS `total` (time DATETIME PRIMARY KEY NOT NULL, total_students INT NOT NULL, total_staff INT NOT NULL);'
        c.execute(sql)
        sql = f'CREATE TABLE IF NOT EXISTS `new` (time DATETIME PRIMARY KEY NOT NULL, new_students INT NOT NULL, new_staff INT NOT NULL);'
        c.execute(sql)
        sql = f'CREATE TABLE IF NOT EXISTS `quarantine` (time DATETIME PRIMARY KEY NOT NULL, quarantine_on_campus INT NOT NULL, quarantine_off_campus INT NOT NULL);'
        c.execute(sql)
        sql = f'CREATE TABLE IF NOT EXISTS `isolation` (time DATETIME PRIMARY KEY NOT NULL, isolation_on_campus INT NOT NULL, isolation_off_campus INT NOT NULL);'
        c.execute(sql)
        sql = f'CREATE TABLE IF NOT EXISTS `beds` (time DATETIME PRIMARY KEY NOT NULL, beds_available INT NOT NULL);'
        c.execute(sql)
        sql = f'CREATE TABLE IF NOT EXISTS `tests` (time DATETIME PRIMARY KEY NOT NULL, tests_administered INT NOT NULL);'
        c.execute(sql)
        db_conn.commit()
        db_conn.close()

def update_db():
    with db_lock:
        db_conn = sqlite3.connect('data/data.sqlite3')
        c = db_conn.cursor()
        sql = f'INSERT INTO `alertlevel` VALUES (datetime(\'now\'), \'{LATEST_DATA["alert_level"]}\');'
        c.execute(sql)
        sql = f'INSERT INTO `total` VALUES (datetime(\'now\'), {LATEST_DATA["total_students"]}, {LATEST_DATA["total_staff"]});'
        c.execute(sql)
        sql = f'INSERT INTO `new` VALUES (datetime(\'now\'), {LATEST_DATA["new_students"]}, {LATEST_DATA["new_staff"]});'
        c.execute(sql)
        sql = f'INSERT INTO `quarantine` VALUES (datetime(\'now\'), {LATEST_DATA["quarantine_on_campus"]}, {LATEST_DATA["quarantine_off_campus"]});'
        c.execute(sql)
        sql = f'INSERT INTO `isolation` VALUES (datetime(\'now\'), {LATEST_DATA["isolation_on_campus"]}, {LATEST_DATA["isolation_off_campus"]});'
        c.execute(sql)
        sql = f'INSERT INTO `beds` VALUES (datetime(\'now\'), {LATEST_DATA["beds_available"]});'
        c.execute(sql)
        sql = f'INSERT INTO `tests` VALUES (datetime(\'now\'), {LATEST_DATA["tests_administered"]});'
        c.execute(sql)
        db_conn.commit()
        db_conn.close()

def get_latest_from_db():
    with db_lock:
        db_conn = sqlite3.connect('data/data.sqlite3')
        c = db_conn.cursor()
        sql = 'SELECT max(alertlevel.time), alertlevel.color, total.total_students, total.total_staff, new.new_students, new.new_staff, ' + \
            'quarantine.quarantine_on_campus, quarantine.quarantine_off_campus, isolation.isolation_on_campus, isolation.isolation_off_campus, ' + \
            'beds.beds_available, tests.tests_administered ' + \
            'FROM `alertlevel` ' + \
            'INNER JOIN `total` ' + \
            'ON alertlevel.time = total.time ' + \
            'INNER JOIN `new` ' + \
            'ON alertlevel.time = new.time ' + \
            'INNER JOIN `quarantine` ' + \
            'ON alertlevel.time = quarantine.time ' + \
            'INNER JOIN `isolation` ' + \
            'ON alertlevel.time = isolation.time ' + \
            'INNER JOIN `beds` ' + \
            'ON alertlevel.time = beds.time ' + \
            'INNER JOIN `tests` ' + \
            'ON alertlevel.time = tests.time'
        c.execute(sql)
        d = c.fetchone()

        data = {
            'alert_level': d[1],        
            'total_students': d[2],
            'total_staff': d[3],
            'new_students': d[4],
            'new_staff': d[5],
            'quarantine_on_campus': d[6],
            'quarantine_off_campus': d[7],
            'isolation_on_campus': d[8],
            'isolation_off_campus': d[9],
            'beds_available': d[10],
            'tests_administered': d[11],
            'last_updated': d[0]
        }
        return data

def get_all_from_db():
    with db_lock:
        db_conn = sqlite3.connect('data/data.sqlite3')
        c = db_conn.cursor()
        sql = 'SELECT alertlevel.time, alertlevel.color, total.total_students, total.total_staff, new.new_students, new.new_staff, ' + \
            'quarantine.quarantine_on_campus, quarantine.quarantine_off_campus, isolation.isolation_on_campus, isolation.isolation_off_campus, ' + \
            'beds.beds_available, tests.tests_administered ' + \
            'FROM `alertlevel` ' + \
            'INNER JOIN `total` ' + \
            'ON alertlevel.time = total.time ' + \
            'INNER JOIN `new` ' + \
            'ON alertlevel.time = new.time ' + \
            'INNER JOIN `quarantine` ' + \
            'ON alertlevel.time = quarantine.time ' + \
            'INNER JOIN `isolation` ' + \
            'ON alertlevel.time = isolation.time ' + \
            'INNER JOIN `beds` ' + \
            'ON alertlevel.time = beds.time ' + \
            'INNER JOIN `tests` ' + \
            'ON alertlevel.time = tests.time'
        c.execute(sql)

        data = [{
            'alert_level': d[1],        
            'total_students': d[2],
            'total_staff': d[3],
            'new_students': d[4],
            'new_staff': d[5],
            'quarantine_on_campus': d[6],
            'quarantine_off_campus': d[7],
            'isolation_on_campus': d[8],
            'isolation_off_campus': d[9],
            'beds_available': d[10],
            'tests_administered': d[11],
            'last_updated': d[0]
        } for d in c.fetchall()]
        return data

def data_is_same(current_data):
    global LATEST_DATA
    if LATEST_DATA is None or current_data is None:
        return False
    for key in list(LATEST_DATA.keys()):
        if key != 'last_updated' and current_data[key] != LATEST_DATA[key]:
            return False
    return True

def db_is_same(current_data):
    latest_data = get_latest_from_db()
    if latest_data is None or current_data is None:
        return False
    for key in list(latest_data.keys()):
        if key != 'last_updated' and current_data[key] != latest_data[key]:
            return False
    return True

def get_data():
    global data_thread
    data_thread = threading.Timer(POOL_TIME, get_data, ())
    data_thread.start()
    create_tables()
    page = requests.get(DASHBOARD_URL, headers={'Cache-Control': 'no-cache'})
    soup = BeautifulSoup(page.content, 'html.parser')
    total_students = int(soup.find('div', attrs={'class': 'statistic-12481'}).find_all("p", attrs={'class': 'card-header'})[0].text.strip())
    total_staff = int(soup.find('div', attrs={'class': 'statistic-12484'}).find_all("p", attrs={'class': 'card-header'})[0].text.strip())
    new_students = int(soup.find('div', attrs={'class': 'statistic-12202'}).find_all("p", attrs={'class': 'card-header'})[0].text.strip())
    new_staff = int(soup.find('div', attrs={'class': 'statistic-12205'}).find_all("p", attrs={'class': 'card-header'})[0].text.strip())
    quarantine_on_campus = int(soup.find('div', attrs={'class': 'statistic-12190'}).find_all("p", attrs={'class': 'card-header'})[0].text.strip())
    quarantine_off_campus = int(soup.find('div', attrs={'class': 'statistic-12193'}).find_all("p", attrs={'class': 'card-header'})[0].text.strip())
    isolation_on_campus = int(soup.find('div', attrs={'class': 'statistic-12226'}).find_all("p", attrs={'class': 'card-header'})[0].text.strip())
    isolation_off_campus = int(soup.find('div', attrs={'class': 'statistic-12229'}).find_all("p", attrs={'class': 'card-header'})[0].text.strip())
    beds_available = int(soup.find('div', attrs={'class': 'statistic-12214'}).find_all("p", attrs={'class': 'card-header'})[0].text.strip().strip('%'))
    tests_administered = int(soup.find('div', attrs={'class': 'statistic-12829'}).find_all("p", attrs={'class': 'card-header'})[0].text.strip().replace("*", " "))
    container = soup.find('div', attrs={'id': 'pandemic-message-container'})
    alert_level = container.find("a").text
    color = ""
    if "Green" in alert_level:
        color = 'green'
    elif "Yellow" in alert_level:
        color = 'yellow'
    elif "Orange" in alert_level:
        color = 'orange'
    elif "Red" in alert_level:
        color = 'red'
    global LATEST_DATA
    current_data = {
        'alert_level': color,        
        'total_students': total_students,
        'total_staff': total_staff,
        'new_students': new_students,
        'new_staff': new_staff,
        'quarantine_on_campus': quarantine_on_campus,
        'quarantine_off_campus': quarantine_off_campus,
        'isolation_on_campus': isolation_on_campus,
        'isolation_off_campus': isolation_off_campus,
        'beds_available': beds_available,
        'tests_administered': tests_administered,
        'last_updated': str(datetime.datetime.now()).replace('GMT', 'EST')
    }
    LATEST_DATA = current_data
    if not db_is_same(current_data):
        update_db()
    return current_data


get_data()
# When you kill Flask (SIGTERM), clear the trigger for the next thread
atexit.register(interrupt)


APP = Flask(__name__)

# Load file based configuration overrides if present
if os.path.exists(os.path.join(os.getcwd(), 'config.py')):
    APP.config.from_pyfile(os.path.join(os.getcwd(), 'config.py'))
else:
    APP.config.from_pyfile(os.path.join(os.getcwd(), 'config.env.py'))

APP.secret_key = APP.config['SECRET_KEY']

@APP.route('/api/v0/latest')
def _api_v0_latest():
    return jsonify(LATEST_DATA)

@APP.route('/api/v0/latestdb')
def _api_v0_latestdb():
    data = get_latest_from_db()
    return jsonify(data)

@APP.route('/api/v0/history')
def _api_v0_history():
    data = get_all_from_db()
    return jsonify(data)
