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

def data_is_same(current_data):
    global LATEST_DATA
    if LATEST_DATA is None or current_data is None:
        return False
    for key in list(LATEST_DATA.keys()):
        if current_data[key] != LATEST_DATA[key] and key != 'last_updated':
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
        'last_updated': datetime.datetime.now()
    }
    if not data_is_same(current_data):
        LATEST_DATA = current_data


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

@APP.route('/api/v1/latest')
def _index():
    return jsonify(LATEST_DATA)
