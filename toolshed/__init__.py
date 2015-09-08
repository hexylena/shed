#!/usr/bin/env python
import os
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask_jwt import JWT


# Config
current_path = os.path.dirname(__file__)
client_path = os.path.abspath(os.path.join(current_path, '..', 'frontend'))

app = Flask(
    __name__,
    static_url_path='',
    static_folder=client_path
)
app.config.from_object('toolshed.config')
upload_path = os.path.abspath(app.config['UPLOAD_PATH'])
if not os.path.exists:
    os.mkdir(upload_path)

jwt = JWT(app)
db = SQLAlchemy(app)

import toolshed.models  # noqa
import toolshed.views  # noqa
