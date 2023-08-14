from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func


class UserData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    Name = db.Column(db.String(100))
    email = db.Column(db.String(150))
    resume_score = db.Column(db.String(100))
    Timestamp = db.Column(db.DateTime(timezone=True), default=func.now())
    Page_no = db.Column(db.String(100))
    Predicted_Field = db.Column(db.String(100) , default="Not Yet")
    User_level = db.Column(db.String(100))
    Actual_skills = db.Column(db.String(1000))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    job_id = db.Column(db.Integer, db.ForeignKey('job.id'))


class Job(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    Required_skills = db.Column(db.String(1000))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    candidates = db.relationship('UserData')

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    category = db.Column(db.String(150))
    password = db.Column(db.String(150))
    first_name = db.Column(db.String(150))
    cvData = db.relationship('UserData')
    jobs = db.relationship('Job')
