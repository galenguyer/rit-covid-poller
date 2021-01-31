import threading
import sqlite3

db_lock = threading.Lock()

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


def get_latest_from_db():
    return get_all_from_db()[-1]

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
