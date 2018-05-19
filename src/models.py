from app import DB
from datetime import datetime

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
