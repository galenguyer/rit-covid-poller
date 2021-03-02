"""
CLI commands for data management
"""
import json
import click
from dateutil import parser

from . import APP, db
from .models import Day

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
