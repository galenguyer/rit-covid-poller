"""
Startup code
"""

import os
import json
import logging
import datetime
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

APP = Flask(__name__)

# Load default configuration and any environment variable overrides
_root_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
APP.config.from_pyfile(os.path.join(_root_dir, 'config.env.py'))

# Load file based configuration overrides if present
_pyfile_config = os.path.join(_root_dir, 'config.py')
if os.path.exists(_pyfile_config):
    APP.config.from_pyfile(_pyfile_config)

# Logger configuration
logging.getLogger().setLevel(APP.config['LOG_LEVEL'])
#pylint: disable=no-member
APP.logger.info('Launching rit-covid-poller v' + APP.config['VERSION'])

db = SQLAlchemy(APP)
migrate = Migrate(APP, db)
APP.logger.info('SQLAlchemy pointed at ' + repr(db.engine.url))
#pylint: enable=no-member

#pylint: disable=wrong-import-position
from . import models
from . import commands
from . import routes

db.create_all()
