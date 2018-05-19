import os
from sqlalchemy import exc
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, request, jsonify

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
channels = {}

def get_channel(channel_name):
    channel_id = None
    if channel_name in channels:
        channel_id = channels[channel_name]
    else:
        channel = Channel.query.filter_by(name=channel_name)
        if channel:
            channels[channel_name] = channel.id
            channel_id = channels[channel_name]
    return channel_id

def add_channel(channel_name):
    channel = Channel(name=channel_name)
    try:
        DB.session.add(channel)
        DB.session.commit()
        return 200
    except (exc.SQLAlchemyError, exc.DBAPIError):
        DB.session.rollback()
        return 404


#--------- Functions for Log ---------#
def get_logs(channel_name):
    '''
    Returns relevant Logs in JSON format
    '''
    msges = []
    channel_id = get_channel(channel_name)
    if not channel_id:
        return 404
    logs = Logs.query.filter_by(channel_id=channel_id)
    for msg in logs:
        msges.append(msg.to_json())
    return jsonify(msges)

def add_logs(channel_name):
    '''
    Reads input from message field of POST request
    and adds it to Logs table
    '''
    channel_id = get_channel(channel_name)
    if not channel_id:
        add_channel(channel_name)
        channel_id = get_channel(channel_name)
    log_entry = Logs(msg=request.form['message'], channel_id=channel_id)
    try:
        DB.session.add(log_entry)
        DB.session.commit()
        return 200
    except (exc.SQLAlchemyError, exc.DBAPIError):
        DB.session.rollback()
        return 404


#---------Controller for Logs --------#
@APP.route('/logs/<channel_name>', methods=['GET', 'POST'])
@login_required
def logs(channel_name):
    if not channel_name:
        return 404
    elif request.method == 'GET':
        return get_logs(channel_name)
    elif request.method == 'POST':
        return add_logs(channel_name)

#-------- Initialize db and APP ---------#
if __name__ == '__main__':
    init_db()
    APP.run()
