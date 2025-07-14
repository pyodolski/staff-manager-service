# models.py
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    google_id = db.Column(db.String(100), unique=True, nullable=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    name = db.Column(db.String(100))
    picture = db.Column(db.String(200))
    role = db.Column(db.SmallInteger, default=0)
@property
def is_active(self):
    return True

from datetime import datetime
from models import db

class WorkLog(db.Model):
    __tablename__ = 'worklog'  # 실제 테이블명과 맞춰주세요

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    work_date = db.Column(db.Date, nullable=False)
    clock_in = db.Column(db.Time, nullable=False)
    clock_out = db.Column(db.Time, nullable=False)
    total_hours = db.Column(db.Float, nullable=False)
    status = db.Column(db.SmallInteger, nullable=False, default=0)  # 0: 대기, 1: 승인
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
