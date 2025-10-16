from flask import Flask
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from markupsafe import escape, Markup

app = Flask(__name__)

@app.template_filter()
def nl2br(value):
    """Converte quebras de linha em tags <br> para exibição em HTML."""

    escaped_value = escape(value)
    result = escaped_value.replace('\n', Markup('<br>\n'))
    return result

app.config.from_object('app.configuration.DevelopmentConfig')

bs = Bootstrap(app)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
lm = LoginManager()
lm.init_app(app)
lm.login_view = 'login' 

from app import models, views