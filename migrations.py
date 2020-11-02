import os
import csv
import sqlite3

LATEST_DATA={}

def create_tables():
    print('creating tables')
    db_conn = sqlite3.connect('./data/data.sqlite3')
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

def get_latest_from_db():

    db_conn = sqlite3.connect('./data/data.sqlite3')
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

with open('historical_data.csv', 'r') as csvfile:
    print('importing data...')
    csvreader = csv.reader(csvfile)
    firstRow = True
    for row in csvreader:
        if firstRow: 
            firstRow = False
            continue
        LATEST_DATA = {
            'alert_level': str(row[1]),        
            'total_students': int(row[4]),
            'total_staff': int(row[5]),
            'new_students': int(row[2]),
            'new_staff': int(row[3]),
            'quarantine_on_campus': int(row[6]),
            'quarantine_off_campus': int(row[7]),
            'isolation_on_campus': int(row[8]),
            'isolation_off_campus': int(row[9]),
            'beds_available': int(row[11]),
            'tests_administered': int(row[10]),
            'last_updated': f'{row[0]} 16:00:00'
        }
        if not db_is_same():
            update_db()
    print('data imported!')
        
