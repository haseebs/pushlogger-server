from app import DB
from datetime import datetime

class Channel(DB.Model):
    id = DB.Column(DB.Integer, autoincrement=True, primary_key=True)
    name = DB.Column(DB.String(16), unique=True, index=True)
    timestamp = DB.Column(DB.DateTime, default=datetime.utcnow)
    logs = DB.relationship("Logs", cascade="all,delete", backref="author",
                           lazy="dynamic")

    def __repr__(self):
        return '<Channel Name: {}>'.format(self.name)

    def to_json(self):
        return {
            "Id": self.id,
            "Channel Name": self.name,
            "Timestamp": self.timestamp.strftime("%H:%M:%S"),
        }

class Logs(DB.Model):
    id = DB.Column(DB.Integer, primary_key=True)
    msg = DB.Column(DB.String(128))
    timestamp = DB.Column(DB.DateTime, default=datetime.utcnow)
    channel_id = DB.Column(DB.Integer, DB.ForeignKey(Channel.id, ondelete="CASCADE"))

    def __repr__(self):
        return '<Log Message: {}>'.format(self.msg)

    def to_json(self):
        return {
            "Id": self.id,
            "Channel id": self.channel_id,
            "Message": self.msg,
            "Timestamp": self.timestamp.strftime("%H:%M:%S"),
        }

def init_db():
    '''
    Create all tables
    '''
    DB.create_all()
    DB.session.commit()

if __name__ == '__main__':
    init_db()
