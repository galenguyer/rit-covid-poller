"""
CLI commands for data management
"""
import json
import click
import time
import requests
import datetime
from dateutil import parser
from bs4 import BeautifulSoup

from . import APP, db
from .models import Day
DASHBOARD_URL = 'https://www.rit.edu/ready/spring-2022-dashboard'


@APP.cli.command('import-history')
@click.argument('history_file')
def import_history(history_file):
    """
    Import history from JSON file
    """
    data = '{}'
    with open(history_file, 'r') as file:
        data = file.read()
    parsed = json.loads(data)
    for item in parsed:
        if not parser.parse(item['last_updated']) in [day.last_updated for day in Day.get_all()]:
            db.session.add(Day(
                last_updated=parser.parse(item['last_updated']),
                alert_level=item['alert_level'],
                beds_available=item['beds_available'],
                isolation_off_campus=item['isolation_off_campus'],
                isolation_on_campus=item['isolation_on_campus'],
                new_staff=item['new_staff'],
                new_students=item['new_students'],
                quarantine_off_campus=item['quarantine_off_campus'],
                quarantine_on_campus=item['quarantine_on_campus'],
                tests_administered=item['tests_administered'],
                total_staff=item['total_staff'],
                total_students=item['total_students']))
    db.session.commit()


@APP.cli.command('scrape')
def scrape():
    while True:
        get_data()
        time.sleep(5*60)

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
    page = requests.get(DASHBOARD_URL, headers={'Cache-Control': 'no-cache'})
    soup = BeautifulSoup(page.content, 'html.parser')
    total_students = int(soup.find('div', attrs={'class': 'statistic-16128'}).find_all("p", attrs={'class': 'card-header'})[0].text.strip())
    total_staff = int(soup.find('div', attrs={'class': 'statistic-16131'}).find_all("p", attrs={'class': 'card-header'})[0].text.strip())
    new_students = int(soup.find('div', attrs={'class': 'statistic-16116'}).find_all("p", attrs={'class': 'card-header'})[0].text.strip())
    new_staff = int(soup.find('div', attrs={'class': 'statistic-16119'}).find_all("p", attrs={'class': 'card-header'})[0].text.strip())
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
        total_staff=total_staff,
        total_students=total_students)
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
