import os
from sqlalchemy import exc
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, request, jsonify

#------------ Config ----------------#
APP = Flask(__name__)
DB = SQLAlchemy(APP)
MIGRATE = Migrate(APP, DB)
APP.secret_key = '12345'
from models import *
SQLALCHEMY_TRACK_MODIFICATIONS = False
BASEDIR = os.path.abspath(os.path.dirname(__file__))
SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
                          'sqlite:///' + os.path.join(BASEDIR, 'pushlogger.db')

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
        return "Success"
    except (exc.SQLAlchemyError, exc.DBAPIError):
        DB.session.rollback()
        return "Fail"

#--------- REST Controller for Logs --------#
@APP.route('/logs/', methods=['GET', 'POST'])
def logs():
    if request.method == 'GET':
        return get_logs()
    elif request.method == 'POST':
        return add_logs()

#-------- Initialize db and APP ---------#
if __name__ == '__main__':
    init_db()
    APP.run()
