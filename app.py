from models.user import User
from flask import Flask
from flask_migrate import Migrate
from flask_login import LoginManager

from routes.index import index_routes
from routes.auth import auth
from routes.classes import classes
from db import db

app = Flask(__name__)

app.config['SECRET_KEY'] = 'this_is_supposed_to_be_very_very_secret'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///qrdb.db'

db.init_app(app)
Migrate(app, db)

login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    # since the user_id is just the primary key of our user table,
    # use it in the query for the user
    return User.query.get(user_id)


app.register_blueprint(index_routes)
app.register_blueprint(auth)
app.register_blueprint(classes)


# app.run(debug=True)
