
from flask import Flask
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate

app = Flask(__name__)

app.config.from_object('app.configuration.DevelopmentConfig')

bs = Bootstrap(app) #flask-bootstrap
db = SQLAlchemy(app) #flask-sqlalchemy
migrate = Migrate(app, db)

lm = LoginManager()
lm.init_app(app)
lm.login_view = 'login'

from app import views, models