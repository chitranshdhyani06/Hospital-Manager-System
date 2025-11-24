from flask import Flask
from application.database import db
from datetime import date, timedelta, datetime

app = None

def create_app():
  app = Flask(__name__)
  app.debug = True
  app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///doctor.sqlite3'
  db.init_app(app)
  app.app_context().push()
  return app

app = create_app()
from application.controllers import *

if __name__ == '__main__':
  db.create_all()
  Admin = User.query.filter_by(username="admin").first()
  time = Time.query.first()
  if Admin is None:
    Admin = User(username = "admin", name="Admin1", email="admin1@gmail.com", password="admin123", gender="Male", type="admin")
    db.session.add(Admin)
    db.session.commit()
  
  if time is None:
    start = date(2025, 11, 16)
    for i in range(1, 8):
      current = start + timedelta(days=i)
      slot_time1 = "08:00 A.M-12:00 P.M"
      slot_time2 = "04:00 P.M-08:00 P.M"
      time_slot1 = Time(date=current, time=slot_time1)
      time_slot2 = Time(date=current, time=slot_time2)
      db.session.add(time_slot1)
      db.session.add(time_slot2)
      db.session.commit()



  app.run()

