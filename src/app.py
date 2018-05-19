import os
from sqlalchemy import exc
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, request, jsonify
from flask_login import LoginManager, current_user, login_user, logout_user, login_required
from werkzeug.security import generate_password_hash

#------------ Config ----------------#
APP = Flask(__name__)
#DB
DB = SQLAlchemy(APP)
MIGRATE = Migrate(APP, DB)
APP.secret_key = '12345'
from models import *
SQLALCHEMY_TRACK_MODIFICATIONS = False
BASEDIR = os.path.abspath(os.path.dirname(__file__))
SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
                          'sqlite:///' + os.path.join(BASEDIR, 'pushlogger.db')
#Login
LOGIN_MANAGER = LoginManager()
LOGIN_MANAGER.init_app(APP)
@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

#--------- Functions for Log ---------#
def get_logs():
    '''
    Returns relevant Logs in JSON format
    '''
    msges = []
    logs = Logs.query.all()
    for msg in logs:
        msges.append(msg.to_json())
    return jsonify(msges)

def add_logs():
    '''
    Reads input from message field of POST request
    and adds it to Logs table
    '''
    log_entry = Logs(msg=request.form['message'])
    try:
        DB.session.add(log_entry)
        DB.session.commit()
        return 200
    except (exc.SQLAlchemyError, exc.DBAPIError):
        DB.session.rollback()
        return 404

#--------- Functions for User ---------#
def login():
     if current_user.is_authenticated:
         return 200
     elif request.form.get('email'):
         user = User.query.filter_by(email=request.form.get('email')).first()
         if user is not None and user.check_password(request.form.get('password')):
             login_user(user, remember=True)
             return 200
     return 404

 def logout():
     logout_user()
     return 200

 def register():
    if current_user.is_authenticated:
        return 200
    elif request.form.get('email'):
        user = User(email=request.form.get('email'))
        user.set_password(request.form.get('password'))
        try:
            db.session.add(user)
            db.session.commit()
            login_user(user, remember=True)
            return 200
        except (exc.SQLAlchemyError, exc.DBAPIError):
            db.session.rollback()
    return 404

#---------Controller for Logs --------#
@APP.route('/logs/', methods=['GET', 'POST'])
@login_required
def logs():
    if request.method == 'GET':
        return get_logs()
    elif request.method == 'POST':
        return add_logs()

#---------Controllers for User --------#
@APP.route('/user/login', methods=['POST'])
def user_login():
    return login()

@APP.route('/user/logout')
def user_logout():
    return logout()

@APP.route('/user/register', methods=['POST'])
def user_register():
    return register()

#-------- Initialize db and APP ---------#
if __name__ == '__main__':
    init_db()
    APP.run()
