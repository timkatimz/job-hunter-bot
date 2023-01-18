from setup_db import db


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, nullable=False)
    chat_id = db.Column(db.Integer, nullable=False)
    username = db.Column(db.String(50))
    position = db.Column(db.String(25), nullable=False)
    is_active = db.Column(db.Boolean(), default=True)
