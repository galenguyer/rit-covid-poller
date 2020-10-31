""" A small flask Hello World """

import os
import threading
import sqlite3
import atexit

from flask import Flask, jsonify

POOL_TIME = 5 * 60 # Seconds
DASHBOARD_URL = 'https://rit.edu/ready/dashboard'
db_lock = threading.Lock()

if not os.path.exists('./data'):
    os.mkdir('./data')

def interrupt():
    global ping_thread
    ping_thread.cancel()

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
        sql = f'CREATE TABLE IF NOT EXISTS `isolation` (time DATETIME PRIMARY KEY NOT NULL, isolation_on_campus INT NOT NULL, isolation_off_campus INT NOT NULL);'
        c.execute(sql)
        sql = f'CREATE TABLE IF NOT EXISTS `beds` (time DATETIME PRIMARY KEY NOT NULL, beds_available INT NOT NULL);'
        c.execute(sql)
        sql = f'CREATE TABLE IF NOT EXISTS `tests` (time DATETIME PRIMARY KEY NOT NULL, tests_administered INT NOT NULL);'
        c.execute(sql)
        db_conn.commit()
        db_conn.close()

def ping_sites():
    global ping_thread
    ping_thread = threading.Timer(POOL_TIME, ping_sites, ())
    ping_thread.start()
    create_tables()
    
ping_sites()
# When you kill Flask (SIGTERM), clear the trigger for the next thread
atexit.register(interrupt)


APP = Flask(__name__)

# Load file based configuration overrides if present
if os.path.exists(os.path.join(os.getcwd(), 'config.py')):
    APP.config.from_pyfile(os.path.join(os.getcwd(), 'config.py'))
else:
    APP.config.from_pyfile(os.path.join(os.getcwd(), 'config.env.py'))

APP.secret_key = APP.config['SECRET_KEY']

@APP.route('/')
def _index():
    return jsonify(status=200, response="OK")
