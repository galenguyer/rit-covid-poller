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
