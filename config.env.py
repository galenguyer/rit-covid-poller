"""
Default configuration settings and environment variable based configuration logic
    See the readme for more information
"""

from os import environ
import secrets

# Flask config
DEBUG = False
IP = environ.get('POLLER_IP', 'localhost')
PORT = environ.get('POLLER_PORT', '5000')
SECRET_KEY = environ.get('POLLER_SECRET_KEY', default=''.join(secrets.token_hex(16)))
LOG_LEVEL = environ.get('PACKET_LOG_LEVEL', 'INFO')
VERSION = '0.1.0'

# SQLAlchemy config
SQLALCHEMY_DATABASE_URI = environ.get('POLLER_DATABASE_URI', 'sqlite:////tmp/rit-covid-poller.db')
SQLALCHEMY_TRACK_MODIFICATIONS = False
