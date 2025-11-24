from flask import Flask, render_template, redirect, request
from flask import current_app as app
from application.models import *
from sqlalchemy import func, or_, and_

@app.route("/")
def index():
  return render_template("/index.html")

@app.route("/login", methods=["GET", "POST"])
def login():
  if request.method == "POST":
    username = request.form["username"]
    pwd = request.form.get("pwd")
    this_user = User.query.filter_by(username=username).first()
    this_doc = Doctor.query.filter_by(id=username).first()
    if this_user:
      if this_user.password == pwd:
        if this_user.type == "admin": 
          return redirect("/admin_dash")
        elif this_user.type == "Patient":
          return redirect(f"/home/{this_user.id}")
        else:
          return render_template("/blacklisted.html")
      else:
        return render_template("incorrect-pass.html")
    elif this_doc:
      if this_doc.doctor_pass == pwd:
        if this_doc.type == "Doctor":
          return redirect(f"/dashboard/{this_doc.id}")
        else:
          return render_template("/blacklisted.html")
      else:
        return render_template("incorrect-pass.html")
    else:
      return render_template("not-exist.html")
  
  return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
  if request.method == "POST":
    username = request.form.get("username")
    name = request.form.get("name")
    email = request.form.get("email")
    pwd = request.form.get("pwd")
    gender = request.form.get("gender")
    user_name = User.query.filter_by(username=username).first()
    user_email = User.query.filter_by(email=email).first()
    if user_name or user_email:
      return render_template("already-exist.html")
    else:
      new_user = User(username=username,name=name,email=email,password=pwd,gender=gender)
      db.session.add(new_user)
      db.session.commit()
      return render_template("login.html")
  return render_template("register.html")

@app.route("/admin_search", methods=["GET", "POST"])
def a_search():
  if request.method == "POST":
    variable = request.form.get("search")
    doctors = Doctor.query.filter(and_(Doctor.type=="Doctor",or_(Doctor.id==variable,Doctor.doctor_name==variable,Doctor.doctor_specs==variable,))).all()
    patients = User.query.filter(and_(User.type=="Patient", or_(User.name==variable, User.id==variable))).all()
    return render_template("search_result.html", doctors=doctors, patients=patients)
    
@app.route("/admin_dash")
def admin():
  all_doctor = Doctor.query.all()
  all_user = User.query.filter(User.type != "admin").all()
  appoint = Appointment.query.all()
  return render_template("admin_dash.html", all_user=all_user, all_doctor=all_doctor, made_appointment=appoint)

@app.route("/add_doctor", methods=["GET", "POST"])
def add_doc():
  if request.method == "POST":
    id = request.form.get("id")
    doctor_pass = request.form.get("pwd")
    doctor_name = request.form.get("name")
    doctor_specs = request.form.get("specs")
    doctor_exp = request.form.get("exp")
    doc_id = Doctor.query.filter_by(id = id).first()
    if doc_id:
      return render_template("already-exist.html")
    else:
      new_doc = Doctor(id=id,doctor_pass=doctor_pass,doctor_name=doctor_name,doctor_specs=doctor_specs,doctor_exp=doctor_exp)
      db.session.add(new_doc)
      db.session.commit()
      return redirect("/admin_dash")
  return render_template("add-new-doctor.html")

@app.route("/home/<int:user_id>", methods=["POST", "GET"])
def home(user_id):
  this_user = User.query.filter_by(id=user_id).first()
  all_doctor = Doctor.query.all()
  detail = (Doctor.query.with_entities(Doctor.doctor_specs,func.count(Doctor.id).label('num_doctors')).group_by(Doctor.doctor_specs).all())
  user_appoint = Appointment.query.filter(Appointment.user_id==user_id).all()
  return render_template("patient-dash.html", this_user=this_user, all_doctor=all_doctor, detail=detail, user_appoint=user_appoint)

@app.route("/dashboard/<doctor_id>")
def dashboard(doctor_id):
  this_doctor = Doctor.query.filter_by(id=doctor_id).first()
  upcoming_appointment = Appointment.query.filter_by(doctor_id=this_doctor.id).all()
  patient = Appointment.query.filter(Appointment.doctor_id == doctor_id).distinct(Appointment.user_id).all()

  return render_template("doctor-dash.html", this_doctor=this_doctor, upcoming_appointment=upcoming_appointment, patient=patient)


@app.route("/button-click/<doctor_id>", methods=['POST'])
def click(doctor_id):
  date = request.form.get("value")
  date_exists = Dates.query.filter(Dates.date == date, Dates.doctor_id == doctor_id).first()
  if not date_exists:
    add_date = Dates(doctor_id=doctor_id, date=date)
    db.session.add(add_date)
    db.session.commit()
  else:
    db.session.delete(date_exists)
    db.session.commit()
  this_doctor = Doctor.query.filter_by(id=doctor_id).first()
  return redirect(f"/availability/{this_doctor.id}")

@app.route("/availability/<doctor_id>")
def availability(doctor_id):
  this_doctor = Doctor.query.filter_by(id=doctor_id).first()
  busy_dates = Dates.query.filter_by(doctor_id=doctor_id).all()
  return render_template("doctor-availability.html",this_doctor=this_doctor, busy_dates=busy_dates)

@app.route("/department/<user_id>/<doctor_specs>")
def view(doctor_specs, user_id):
  this_user = User.query.filter_by(id=user_id).first()
  doctor_exists = Doctor.query.filter_by(doctor_specs=doctor_specs).all()
  doctor_first = Doctor.query.filter_by(doctor_specs=doctor_specs).first()
  return render_template("/department-details.html", doctor_specs=doctor_specs,doctor_exists=doctor_exists, this_user=this_user, doctor_first=doctor_first)

#***************************Date choosed by patient*********************************
@app.route("/availability/<int:user_id>/<doctor_id>")
def availability_user(doctor_id, user_id):
  this_user = User.query.filter_by(id=user_id).first()
  this_doctor = Doctor.query.filter_by(id=doctor_id).first()
  appointment_date = Request.query.filter(Request.doctor_id==doctor_id, Request.user_id==user_id).all()
  busy_dates = Dates.query.filter_by(doctor_id=doctor_id).all()
  return render_template("doctor-availability-user.html",this_doctor=this_doctor, appointment_date=appointment_date, this_user=this_user, busy_dates=busy_dates)

# ************************Date appointment by patient*******************************
@app.route("/click_button/<int:user_id>/<doctor_id>", methods=['POST'])
def user_click(user_id,doctor_id):
  this_user = User.query.filter_by(id=user_id).first()
  this_doctor = Doctor.query.filter_by(id=doctor_id).first()
  date = request.form.get("value")
  date_exist = Dates.query.filter(Dates.date==date, Dates.doctor_id==doctor_id).first()
  if not date_exist :
    date2 = Time.query.filter_by(id=date).first()
    req_exist = Request.query.filter(Request.user_id==user_id, Request.doctor_id==doctor_id, Request.date==date).first()
    appo_exist = Appointment.query.filter(Appointment.doctor_id==doctor_id, Appointment.user_id==user_id, Appointment.date==date2.date, Appointment.time==date2.time).first()
    if not (req_exist and appo_exist):
      add_date = Request(doctor_id=doctor_id, date=date, user_id=user_id)
      appoint = Appointment(doctor_name=this_doctor.doctor_name, doctor_specs=this_doctor.doctor_specs, name=this_user.name, date=date2.date, time=date2.time, doctor_id=this_doctor.id, user_id=this_user.id)
      db.session.add(add_date)
      db.session.add(appoint)
      db.session.commit()
    else:
      db.session.delete(appo_exist)
      db.session.delete(req_exist)
      db.session.commit()
  return redirect(f"/availability/{this_user.id}/{this_doctor.id}")

@app.route("/delete/<doctor_id>")
def delete_doc(doctor_id):
  doc = Doctor.query.filter_by(id=doctor_id).first()
  Request.query.filter_by(doctor_id=doctor_id).delete(synchronize_session=False)
  Dates.query.filter_by(doctor_id=doctor_id).delete(synchronize_session=False)
  Appointment.query.filter_by(doctor_id=doctor_id).delete(synchronize_session=False)

  db.session.delete(doc)
  db.session.commit()
  return redirect("/admin_dash")

@app.route("/delete/<int:user_id>")
def delete_user(user_id):
  user = User.query.filter_by(id=user_id).first()
  Request.query.filter_by(user_id=user_id).delete(synchronize_session=False)
  # History.query.filter_by(user_id=user_id).delete(synchronize_session=False)
  Appointment.query.filter_by(user_id=user_id).delete(synchronize_session=False)

  db.session.delete(user)
  db.session.commit()
  return redirect("/admin_dash")

@app.route("/history/<doctor_id>/<int:user_id>")
def history(doctor_id, user_id):
  this_user = User.query.filter_by(id=user_id).first()
  this_doc = Doctor.query.filter_by(id=doctor_id).first()

  return render_template("/update-history.html", this_user=this_user, this_doc=this_doc)

@app.route("/update/<doctor_id>/<int:user_id>", methods=["POST"])
def update(user_id, doctor_id):
  if request.method == "POST":
    visitnum = request.form.get("visitnum")
    testDone = request.form.get("testdone")
    diagnosis = request.form.get("diagnosis")
    medicine = request.form.get("medicine")
    prescription = request.form.get("prescription")
    history = History(visitnum=visitnum, testDone=testDone, diagnosis=diagnosis, medicine=medicine, prescription=prescription, user_id=user_id)
    db.session.add(history)
    db.session.commit()
  return redirect(f"/dashboard/{doctor_id}")

@app.route("/dashboard/complete/<appoint_id>")
def completed(appoint_id):
  appoint = Appointment.query.filter_by(id=appoint_id).first()
  time_id = Time.query.filter(Time.date==appoint.date, Time.time==appoint.time).first()
  req = Request.query.filter(Request.user_id==appoint.user_id, Request.doctor_id==appoint.doctor_id, Request.date==time_id.id).first()
  
  db.session.delete(appoint)
  db.session.delete(req)
  db.session.commit()
  return redirect(f"/dashboard/{appoint.doctor_id}")

@app.route("/dashboard/cancle/<appoint_id>")
def cancle(appoint_id):
  appoint = Appointment.query.filter_by(id=appoint_id).first()
  time_id = Time.query.filter(Time.date==appoint.date, Time.time==appoint.time).first()
  req = Request.query.filter(Request.user_id==appoint.user_id, Request.doctor_id==appoint.doctor_id, Request.date==time_id.id).first()
  db.session.delete(appoint)
  db.session.delete(req)
  db.session.commit()
  return redirect(f"/dashboard/{appoint.doctor_id}")

@app.route("/cancle_by_user/<appoint_id>")
def cancle_by_user(appoint_id):
  appoint = Appointment.query.filter_by(id=appoint_id).first()
  time_id = Time.query.filter(Time.date==appoint.date, Time.time==appoint.time).first()
  req = Request.query.filter(Request.user_id==appoint.user_id, Request.doctor_id==appoint.doctor_id, Request.date==time_id.id).first()
  db.session.delete(appoint)
  db.session.delete(req)
  db.session.commit()
  return redirect(f"/home/{appoint.user_id}")

@app.route("/view-history/<int:user_id>")
def viewHistory(user_id):
  this_user = User.query.filter_by(id=user_id).first()
  user_his = History.query.filter_by(user_id=user_id).all()
  return render_template("/patient-history.html", user_his=user_his, this_user=this_user)

@app.route("/blacklist/<int:user_id>")
def blacklist_user(user_id):
  this_user = User.query.filter_by(id=user_id).first()
  if this_user.type != 'blacklisted':
    this_user.type = 'blacklisted'
    db.session.commit()
  else:
    this_user.type = 'Patient'
    db.session.commit()
  return redirect("/admin_dash")

@app.route("/blacklist-doc/<doc_id>")
def blacklist_doc(doc_id):
  this_doc = Doctor.query.filter_by(id=doc_id).first()
  if this_doc.type != 'blacklisted':
    this_doc.type = 'blacklisted'
    db.session.commit()
  else:
    this_doc.type = 'Doctor'
    db.session.commit()
  return redirect("/admin_dash")

@app.route("/doctor_detail/<int:user_id>/<doctor_id>")
def doc_detail(doctor_id,user_id):
  this_user = User.query.filter_by(id=user_id).first()
  this_doctor = Doctor.query.filter_by(id=doctor_id).first()
  return render_template("/doc-detail.html", this_doctor=this_doctor, this_user=this_user)