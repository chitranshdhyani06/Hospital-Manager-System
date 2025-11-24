from .database import db
from sqlalchemy.dialects.postgresql import ARRAY

class User(db.Model):
  id = db.Column(db.Integer, primary_key = True)
  username = db.Column(db.String(), unique = True, nullable = False)
  name = db.Column(db.String(), nullable = False)
  email = db.Column(db.String(), unique = True, nullable = False)
  password = db.Column(db.String(), nullable = False)
  gender = db.Column(db.String(), default="Not Defined")
  type = db.Column(db.String(), default="Patient")
  requests=db.relationship("Request", backref="user") 

class Doctor(db.Model):
  id = db.Column(db.String(), primary_key = True)
  doctor_pass = db.Column(db.String(), nullable = False)
  doctor_name = db.Column(db.String(), nullable = False)
  doctor_specs = db.Column(db.String(), nullable = False)
  doctor_exp = db.Column(db.Integer)
  type = db.Column(db.String, default="Doctor")
  requests=db.relationship("Request", backref="doctor")


class Request(db.Model):
  req_id = db.Column(db.Integer, primary_key=True)
  user_id = db.Column(db.Integer(), db.ForeignKey("user.id"), nullable = False)
  doctor_id = db.Column(db.Integer(), db.ForeignKey("doctor.id"), nullable = False)
  date = db.Column(db.Integer(), nullable = False)

class CompletedRequest(db.Model):
  comp_req_id = db.Column(db.Integer, primary_key=True)
  req_id = db.Column(db.Integer(), db.ForeignKey("request.req_id"), nullable=False)
  user_id = db.Column(db.Integer(), db.ForeignKey("user.id"), nullable=False)
  doctor_id  = db.Column(db.Integer(), db.ForeignKey("doctor.id"), nullable=False)
  diagnosis = db.Column(db.Text())
  prescription = db.Column(db.Text())
  medicines = db.Column(db.Text())

class Dates(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  date = db.Column(db.Integer, nullable=False)
  doctor_id  = db.Column(db.String, nullable=False)
  # appointment = db.relationship("Appointment", backref="doctor")

class Time(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  date = db.Column(db.Date(), nullable=False)
  time = db.Column(db.String(), nullable=True)

class Appointment(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  doctor_name = db.Column(db.String(), nullable = False)
  doctor_specs = db.Column(db.String(), nullable = False)
  name = db.Column(db.String(), nullable = False)
  date = db.Column(db.Date(), nullable=False)
  time = db.Column(db.String(), nullable=True)
  status = db.Column(db.String(), default="pending")
  doctor_id  = db.Column(db.Integer(), nullable=False)
  user_id = db.Column(db.Integer(), nullable=False)
  # date_id = db.Column(db.Integer(), db.ForeignKey("date.id"), nullable=False)

class History(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  visitnum = db.Column(db.Integer(), default="-")
  testDone = db.Column(db.String(), default="-")
  diagnosis = db.Column(db.String(), default="-")
  medicine = db.Column(db.String(), default="-")
  prescription = db.Column(db.Text(), default="-")
  user_id = db.Column(db.Integer(), nullable=False)
