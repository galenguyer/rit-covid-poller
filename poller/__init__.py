""" A small flask Hello World """

import os
import threading
import sqlite3
import atexit
import datetime
import json

from flask import Flask, jsonify, request, make_response
import requests
from bs4 import BeautifulSoup

from .dedup import dedup
from .db import create_tables, get_all_from_db, get_latest_from_db

POOL_TIME = 5 * 60 # Seconds
DASHBOARD_URL = 'https://rit.edu/ready/spring-dashboard'
LATEST_DATA = None
data_thread = threading.Thread()
db_lock = threading.Lock()

if not os.path.exists('./data'):
    os.mkdir('./data')

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
        dedup()

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
    total_students = int(soup.find('div', attrs={'class': 'statistic-13872'}).find_all("p", attrs={'class': 'card-header'})[0].text.strip())
    total_staff = int(soup.find('div', attrs={'class': 'statistic-13875'}).find_all("p", attrs={'class': 'card-header'})[0].text.strip())
    #new_students = int(soup.find('div', attrs={'class': 'statistic-12202'}).find_all("p", attrs={'class': 'card-header'})[0].text.strip())
    #new_staff = int(soup.find('div', attrs={'class': 'statistic-12205'}).find_all("p", attrs={'class': 'card-header'})[0].text.strip())
    quarantine_on_campus = int(soup.find('div', attrs={'class': 'statistic-13893'}).find_all("p", attrs={'class': 'card-header'})[0].text.strip())
    quarantine_off_campus = int(soup.find('div', attrs={'class': 'statistic-13896'}).find_all("p", attrs={'class': 'card-header'})[0].text.strip())
    isolation_on_campus = int(soup.find('div', attrs={'class': 'statistic-13905'}).find_all("p", attrs={'class': 'card-header'})[0].text.strip())
    isolation_off_campus = int(soup.find('div', attrs={'class': 'statistic-13908'}).find_all("p", attrs={'class': 'card-header'})[0].text.strip())
    beds_available = int(soup.find('div', attrs={'class': 'statistic-13935'}).find_all("p", attrs={'class': 'card-header'})[0].text.strip().strip('%'))
    tests_administered = int(soup.find('div', attrs={'class': 'statistic-13923'}).find_all("p", attrs={'class': 'card-header'})[0].text.strip().replace("*", " ").replace(",", ""))
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

    fall_data = None
    with open('history/fall-2020.json', 'r') as fd:
        fall_data = json.loads(fd.read())

    current_data = {
        'alert_level': color,        
        'total_students': total_students + fall_data['total_students'],
        'total_staff': total_staff + fall_data['total_staff'],
        'new_students': -1,
        'new_staff': -1,
        'quarantine_on_campus': quarantine_on_campus,
        'quarantine_off_campus': quarantine_off_campus,
        'isolation_on_campus': isolation_on_campus,
        'isolation_off_campus': isolation_off_campus,
        'beds_available': beds_available,
        'tests_administered': tests_administered + fall_data['tests_administered'],
        'last_updated': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    LATEST_DATA = current_data
    if not db_is_same(current_data):
        update_db()
    return current_data

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

@APP.route('/api/v0/difference')
def _api_v0_difference():
    data = get_all_from_db()
    latest = data[-1]
    prev = data[-2]
    data = {
        'alert_level': f'{prev["alert_level"]} -> {latest["alert_level"]}',        
        'total_students': latest["total_students"] - prev["total_students"],
        'total_staff': latest["total_staff"] - prev["total_staff"],
        'new_students': latest["new_students"] - prev["new_students"],
        'new_staff': latest["new_staff"] - prev["new_staff"],
        'quarantine_on_campus': latest["quarantine_on_campus"] - prev["quarantine_on_campus"],
        'quarantine_off_campus': latest["quarantine_off_campus"] - prev["quarantine_off_campus"],
        'isolation_on_campus': latest["isolation_on_campus"] - prev["isolation_on_campus"],
        'isolation_off_campus': latest["isolation_off_campus"] - prev["isolation_off_campus"],
        'beds_available': latest["beds_available"] - prev["beds_available"],
        'tests_administered': latest["tests_administered"] - prev["tests_administered"],
    }
    return jsonify(data)

@APP.route('/api/v0/diff')
def _api_v0_diff():
    first = request.args.get('first')
    last = request.args.get('last')
    data = get_all_from_db()
    if first is None:
        first = 0
    else:
        try:
            first = int(first)
        except:
            first = 0
    if last is None:
        last = len(data) - 1
    else:
        try:
            last = int(last)
        except:
            last = len(data) - 1
    latest = data[last]
    prev = data[first]
    data = {
        'alert_level': f'{prev["alert_level"]} -> {latest["alert_level"]}',        
        'total_students': latest["total_students"] - prev["total_students"],
        'total_staff': latest["total_staff"] - prev["total_staff"],
        'new_students': latest["new_students"] - prev["new_students"],
        'new_staff': latest["new_staff"] - prev["new_staff"],
        'quarantine_on_campus': latest["quarantine_on_campus"] - prev["quarantine_on_campus"],
        'quarantine_off_campus': latest["quarantine_off_campus"] - prev["quarantine_off_campus"],
        'isolation_on_campus': latest["isolation_on_campus"] - prev["isolation_on_campus"],
        'isolation_off_campus': latest["isolation_off_campus"] - prev["isolation_off_campus"],
        'beds_available': latest["beds_available"] - prev["beds_available"],
        'tests_administered': latest["tests_administered"] - prev["tests_administered"],
        'description': f'day {first} to {last}'
    }
    return jsonify(data)

