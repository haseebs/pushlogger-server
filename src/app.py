import os
from sqlalchemy import exc
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, request, jsonify, abort

#------------ Config ----------------#
APP = Flask(__name__)
#DB
DB = SQLAlchemy(APP)
MIGRATE = Migrate(APP, DB)
APP.secret_key = '12345'
from models import *
SQLALCHEMY_TRACK_MODIFICATIONS = False
BASEDIR = os.path.abspath(os.path.dirname(__file__))
DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:///' + os.path.join(BASEDIR, 'pushlogger.db'))
APP.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL

channels = {}

#--------- Functions for Channels ---------#
def get_all_channels():
    channels_json = []
    channels_all = Channel.query.all()
    for channel in channels_all:
        channels_json.append(channel.to_json())
    return jsonify(channels_json)

def get_channel(channel_name, get_full_channel=False):
    if not channel_name in channels or get_full_channel:
        channel = Channel.query.filter_by(name=channel_name).first()
        if not channel:
            return None
        channels[channel_name] = channel.id
        if get_full_channel:
            return channel
    return channels[channel_name]

def add_channel(channel_name):
    channel = Channel(name=channel_name)
    try:
        DB.session.add(channel)
        DB.session.commit()
        return ('', 204)
    except (exc.SQLAlchemyError, exc.DBAPIError):
        DB.session.rollback()
        return ('', 404)

def delete_channel(channel_name):
    channel = get_channel(channel_name, get_full_channel=True)
    try:
        DB.session.delete(channel)
        DB.session.commit()
        return ('', 204)
    except (exc.SQLAlchemyError, exc.DBAPIError):
        DB.session.rollback()
        return ('', 404)

#--------- Functions for Log ---------#
def get_logs(channel_name):
    '''
    Returns relevant Logs in JSON format
    '''
    msges = []
    channel_id = get_channel(channel_name)
    if not channel_id:
        abort(404)
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
    except (exc.SQLAlchemyError, exc.DBAPIError):
        DB.session.rollback()
        abort(404)


#---------Controllers --------#
@APP.route('/logs/<channel_name>', methods=['GET', 'POST'])
def logs_router(channel_name):
    if not channel_name:
        abort(404)
    elif request.method == 'GET':
        return get_logs(channel_name)
    elif request.method == 'POST':
        add_logs(channel_name)
    return ('', 204)

@APP.route('/channels', methods=['GET'])
def channel_router():
    return get_all_channels()

@APP.route('/delete/<channel_name>', methods=['GET'])
def delete_channel_router(channel_name):
    return delete_channel(channel_name)

#-------- Initialize db and APP ---------#
if __name__ == '__main__':
    init_db()
    port = int(os.environ.get('PORT', 5000))
    APP.run(host='0.0.0.0', port=port)
