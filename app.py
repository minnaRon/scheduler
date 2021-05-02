from flask import Flask
from os import getenv

app = Flask(__name__)
app.secret_key = getenv("SECRET_KEY")

import routes, routes_calendar, routes_plan, routes_settings_user, routes_settings_admin