import sqlite3 

def get_all_from_db():
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


def drop_by_date(date):
    db_conn = sqlite3.connect('data/data.sqlite3')
    c = db_conn.cursor()
    sql = f'DELETE FROM `alertlevel` WHERE time=\'{date}\';'
    c.execute(sql)
    sql = f'DELETE FROM `total` WHERE time=\'{date}\';'
    c.execute(sql)
    sql = f'DELETE FROM `new` WHERE time=\'{date}\';'
    c.execute(sql)
    sql = f'DELETE FROM `quarantine` WHERE time=\'{date}\';'
    c.execute(sql)
    sql = f'DELETE FROM `isolation` WHERE time=\'{date}\';'
    c.execute(sql)
    sql = f'DELETE FROM `beds` WHERE time=\'{date}\';'
    c.execute(sql)
    sql = f'DELETE FROM `tests` WHERE time=\'{date}\';'
    c.execute(sql)
    db_conn.commit()
    db_conn.close()


def dedup():
    data = get_all_from_db()
    # get first date
    starting_date = data[-1]['last_updated'].split(' ')[0]
    for i in range(len(data)-2, 0, -1):
        if data[i]['last_updated'].split(' ')[0] != starting_date:
            starting_date = data[i]['last_updated'].split(' ')[0]
        else:
            drop_by_date(data[i]['last_updated'])
            print('dropped ' + data[i]['last_updated'])
