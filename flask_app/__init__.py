# 3rd-party packages
from flask import Flask, render_template, request, redirect, url_for
from flask_mongoengine import MongoEngine
from flask_talisman import Talisman
from flask_login import (
    LoginManager,
    current_user,
    login_user,
    logout_user,
    login_required,
)
from flask_bcrypt import Bcrypt
from werkzeug.utils import secure_filename

# stdlib
import os
from datetime import datetime

# # local
# from .client import ItemClient

app = Flask(__name__)
app.config["MONGODB_HOST"] = "mongodb://localhost:27017/project_4"
app.config["SECRET_KEY"] = os.urandom(16)

app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
)

csp = {
    'default-src': [
        '\'self\''
    ],
    'img-src': ['\'self\'', '*', 'data:'],
    'style-src': [
        '\'self\'',
        'https://stackpath.bootstrapcdn.com/bootstrap/4.4.1/css/bootstrap.min.css'
    ],
    'script-src': [
        '\'self\'',
        'https://code.jquery.com/jquery-3.4.1.slim.min.js',
        'https://cdn.jsdelivr.net/npm/popper.js@1.16.0/dist/umd/popper.min.js',
        'https://stackpath.bootstrapcdn.com/bootstrap/4.4.1/js/bootstrap.min.js'
    ]
}

Talisman(app, content_security_policy=csp)
db = MongoEngine(app)
login_manager = LoginManager(app)
login_manager.login_view = "login"
bcrypt = Bcrypt(app)

# replace "default_value" with your api key if you need to hardcode it
# client = ItemClient(db)

from . import routes
