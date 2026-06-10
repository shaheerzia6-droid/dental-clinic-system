from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    # 'assistant' or 'doctor'
    role = db.Column(db.String(20), default='assistant')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<User {self.username}>'


class Patient(db.Model):
    __tablename__ = 'patients'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    visits = db.relationship('Visit', backref='patient',
                             lazy=True, cascade='all, delete-orphan')


class Visit(db.Model):
    __tablename__ = 'visits'

    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey(
        'patients.id'), nullable=False)
    visit_date = db.Column(db.DateTime, default=datetime.utcnow)
    slip_fee = db.Column(db.Float, default=0.0)
    total_paid = db.Column(db.Float, default=0.0)
    status = db.Column(db.String(20), default='checked_in')
    welcome_sent = db.Column(db.Boolean, default=False)
    thank_you_sent = db.Column(db.Boolean, default=False)

    procedures = db.relationship(
        'Procedure', backref='visit', lazy=True, cascade='all, delete-orphan')


class Procedure(db.Model):
    __tablename__ = 'procedures'

    id = db.Column(db.Integer, primary_key=True)
    visit_id = db.Column(db.Integer, db.ForeignKey(
        'visits.id'), nullable=False)
    procedure_name = db.Column(db.String(200), nullable=False)
    procedure_cost = db.Column(db.Float, default=0.0)
    paid_amount = db.Column(db.Float, default=0.0)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
