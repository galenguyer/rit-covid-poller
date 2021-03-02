"""
Defines models
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime

from . import db

#pylint: disable=too-few-public-methods
class Day(db.Model):
    """
    Model for each day's data
    """
    __tablename__ = 'days'
    last_updated = Column(DateTime, default=datetime.now, onupdate=datetime.now, \
        primary_key=True, nullable=False)
    alert_level = Column(String(16), nullable=False)
    beds_available = Column(Integer, nullable=False)
    isolation_off_campus = Column(Integer, nullable=False)
    isolation_on_campus = Column(Integer, nullable=False)
    new_staff = Column(Integer, nullable=False)
    new_students = Column(Integer, nullable=False)
    quarantine_off_campus = Column(Integer, nullable=False)
    quarantine_on_campus = Column(Integer, nullable=False)
    tests_administered = Column(Integer, nullable=False)
    total_staff = Column(Integer, nullable=False)
    total_students = Column(Integer, nullable=False)

    @classmethod
    def get_all(cls):
        """
        Helper to get all values from the database
        """
        return cls.query.all()

    def serialize(self):
        """
        used for json serialization
        """
        return {
            'last_updated': self.last_updated.strftime('%Y-%m-%d %H:%M:%S'),
            'alert_level': self.alert_level,
            'beds_available': self.beds_available,
            'isolation_off_campus': self.isolation_off_campus,
            'isolation_on_campus': self.isolation_on_campus,
            'new_staff': self.new_staff,
            'new_students': self.new_students,
            'quarantine_off_campus': self.quarantine_off_campus,
            'quarantine_on_campus': self.quarantine_on_campus,
            'tests_administered': self.tests_administered,
            'total_staff': self.total_staff,
            'total_students': self.total_students,
        }
