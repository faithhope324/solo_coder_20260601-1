from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


class Room(db.Model):
    __tablename__ = 'rooms'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(6), unique=True, nullable=False, index=True)
    title = db.Column(db.String(200), nullable=False)
    options = db.Column(db.Text, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    votes = db.relationship('Vote', backref='room', lazy=True, cascade='all, delete-orphan')

    def get_options_list(self):
        return [opt.strip() for opt in self.options.split(',') if opt.strip()]

    def to_dict(self):
        return {
            'code': self.code,
            'title': self.title,
            'options': self.get_options_list(),
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat()
        }


class Vote(db.Model):
    __tablename__ = 'votes'

    id = db.Column(db.Integer, primary_key=True)
    room_id = db.Column(db.Integer, db.ForeignKey('rooms.id'), nullable=False)
    option = db.Column(db.String(200), nullable=False)
    voter_ip = db.Column(db.String(50), nullable=False)
    voter_session = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint('room_id', 'voter_ip', name='uq_room_ip'),
        db.UniqueConstraint('room_id', 'voter_session', name='uq_room_session'),
    )

    def to_dict(self):
        return {
            'option': self.option,
            'created_at': self.created_at.isoformat()
        }
