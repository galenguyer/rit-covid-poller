import os
import json
import sqlite3

from poller.db import create_tables, get_latest_from_db

LATEST_DATA={}

def update_db():
    db_conn = sqlite3.connect('./data/data.sqlite3')
    c = db_conn.cursor()
    sql = f'INSERT INTO `alertlevel` VALUES (\'{LATEST_DATA["last_updated"]}\', \'{LATEST_DATA["alert_level"]}\');'
    c.execute(sql)
    sql = f'INSERT INTO `total` VALUES (\'{LATEST_DATA["last_updated"]}\', {LATEST_DATA["total_students"]}, {LATEST_DATA["total_staff"]});'
    c.execute(sql)
    sql = f'INSERT INTO `new` VALUES (\'{LATEST_DATA["last_updated"]}\', {LATEST_DATA["new_students"]}, {LATEST_DATA["new_staff"]});'
    c.execute(sql)
    sql = f'INSERT INTO `quarantine` VALUES (\'{LATEST_DATA["last_updated"]}\', {LATEST_DATA["quarantine_on_campus"]}, {LATEST_DATA["quarantine_off_campus"]});'
    c.execute(sql)
    sql = f'INSERT INTO `isolation` VALUES (\'{LATEST_DATA["last_updated"]}\', {LATEST_DATA["isolation_on_campus"]}, {LATEST_DATA["isolation_off_campus"]});'
    c.execute(sql)
    sql = f'INSERT INTO `beds` VALUES (\'{LATEST_DATA["last_updated"]}\', {LATEST_DATA["beds_available"]});'
    c.execute(sql)
    sql = f'INSERT INTO `tests` VALUES (\'{LATEST_DATA["last_updated"]}\', {LATEST_DATA["tests_administered"]});'
    c.execute(sql)
    db_conn.commit()
    db_conn.close()

def db_is_same():
    global LATEST_DATA
    latest_data = get_latest_from_db()
    if latest_data is None or LATEST_DATA is None:
        return False
    for key in list(latest_data.keys()):
        if key != 'last_updated' and LATEST_DATA[key] != latest_data[key]:
            return False
    return True

if not os.path.exists('./data'):
    os.mkdir('./data')

create_tables()

with open('history/history.json', 'r') as fd:
    print('importing data...')
    data = json.loads(fd.read())
    for day in data:
        print(day)
        LATEST_DATA = {
            'alert_level': str(day['alert_level']),        
            'total_students': int(day['total_students']),
            'total_staff': int(day['total_staff']),
            'new_students': int(day['new_students']),
            'new_staff': int(day['new_staff']),
            'quarantine_on_campus': int(day['quarantine_on_campus']),
            'quarantine_off_campus': int(day['quarantine_off_campus']),
            'isolation_on_campus': int(day['isolation_on_campus']),
            'isolation_off_campus': int(day['isolation_off_campus']),
            'beds_available': int(day['beds_available']),
            'tests_administered': int(day['tests_administered']),
            'last_updated': day['last_updated']
        }
        update_db()
    print('data imported!')
        
