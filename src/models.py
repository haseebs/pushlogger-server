from app import DB
from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class User(UserMixin, DB.Model):
    id = DB.Column(DB.Integer, primary_key=True)
    email = DB.Column(DB.String(120), unique=True, index=True)
    password_digest = DB.Column(db.String(128))
    logs = DB.relationship('Logs', cascade="all,delete", backref='author', lazy='dynamic')

    def set_password(self, password):
        self.password_digest = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_digest, password)

    def __repr__(self):
        return '<User {}>'.format(self.username)....


class Logs(DB.Model):
    id = DB.Column(DB.Integer, primary_key=True)
    msg = DB.Column(DB.String(128))
    timestamp = DB.Column(DB.DateTime, index=True, default=datetime.utcnow)

    def __repr__(self):
        return '<Log Message: {}>'.format(self.msg)

    def to_json(self):
        return {
            "Id": self.id,
            "Message": self.msg,
            "Timestamp": self.timestamp.strftime("%Y%m%d"),
        }

def init_db():
    '''
    Create all tables
    '''
    DB.create_all()
    DB.session.commit()

if __name__ == '__main__':
    init_db()
