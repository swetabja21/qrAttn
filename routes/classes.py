from annotators import must_be_professor
from flask import (Blueprint, request, redirect,
                   url_for, render_template, flash)
from flask_login import login_required, current_user
import json
import datetime
import pyqrcode
from models.clas import Class
from models.user import User
from models.attendance import Attendance
from db import db
import requests
import geopy.distance
classes = Blueprint("classes", __name__, template_folder="templates")


@ classes.route("/class", methods=["GET"])
@ login_required
@ must_be_professor
def index():
    return render_template("add_class.html")


@classes.route("/class/<cid>", methods=["GET"])
@login_required
def get(cid):
    # user should be a part of the class to view it
    if cid not in json.loads(current_user.class_ids).get("ids", []):
        flash("User should be a part of a class to view it.", "error")
        return redirect(url_for("main.profile"))

    dt = request.args.get("date", default="")

    try:
        if dt is not None and dt != "":
            dt = datetime.datetime.strptime(dt, "%Y-%m-%d").date()
        else:
            dt = datetime.datetime.today().date()
    except ValueError as e:
        print(e)
        flash("Date formate should be yyyy/mm/dd", "error")
        return render_template(url_for("classes.get"))

    cl = Class.query.filter_by(id=cid).first()
    creator = User.query.filter_by(id=cl.creatorId).first()
    present_studentids = Attendance.get_attendance_of_class_on_date(
        str(cl.id), dt)
    all_students = json.loads(cl.studentIds).get("ids", [])
    attendancedata = []
    for st in all_students:
        student = User.query.filter_by(role="student", id=st).first()
        attendancedata.append({
            "name": student.name,
            "present": st in present_studentids
        })
    return render_template("class.html",
                           cl=cl,
                           creator=creator,
                           datenow=str(dt),
                           attendance=attendancedata)


@classes.route("/class/<cid>/seek", methods=["GET"])
@login_required
def seek_attendance(cid):
    # only students can seek attendance
    if current_user.role != "student":
        flash("You must be a student to get attendance for that class", "error")
        return redirect(url_for("main.profile"))

    # check if student belongs to class
    # if not make them belong
    print("here")
    classes = json.loads(current_user.class_ids).get("ids", [])
    if cid not in classes:
        classes.append(cid)
        u = User.query.filter_by(id=str(current_user.id)).first()
        u.class_ids = json.dumps({"ids": classes})
    cl = Class.query.filter_by(
        id=cid,
    ).first()
    print(bool(cl))
    if bool(cl):
        # check if its a valid time to get attendance
        now = datetime.datetime.utcnow() + datetime.timedelta(hours=5, minutes=30)
        if now < cl.startTime or now > cl.endTime:
            flash(
                f"Attendance for this class only available from {cl.startTime} to {cl.endTime}"
                "error"
            )
            return redirect(url_for("main.profile"))
        else:
            ids = json.loads(cl.studentIds).get("ids", [])
            if current_user.id not in ids:
                ids.append(str(current_user.id))
            cl.studentIds = json.dumps({"ids": ids})
    else:
        flash("That class does not exist.", "error")
        return redirect(url_for("main.profile"))

    # check location info of teacher and student
    client_ip = request.remote_addr
    print(client_ip)
    resp = requests.get(f"http://ip-api.com/json/{client_ip}")
    rjson = resp.json()
    print(rjson)
    if rjson['status'] == 'fail':
        flash("Invaid IP to take attendance")
        return redirect(url_for("main.profile"))
    lat = rjson['lat']
    lon = rjson['lon']

    prof = User.query.filter_by(id=cl.creatorId).first()

    loc = json.loads(prof.location)
    plat = loc['lat']
    plon = loc['lon']

    d = geopy.distance.geodesic((lat, lon), (plat, plon)).km

    if d < 0.00762:
        atn = Attendance(cid=cid, sid=str(
            current_user.id), pid=str(cl.creatorId), verified=False)
        db.session.add(atn)
        db.session.commit()
    else:
        flash("Error: you are not within range of ur class")
    return redirect(url_for("main.profile"))


@ classes.route("/class", methods=["POST"])
@ login_required
@ must_be_professor
def class_post():
    name = request.form.get("name")
    start = request.form.get("start")
    end = request.form.get("end")

    if not name:
        flash("Name is required")
        return redirect(url_for("classes.index"))

    try:
        start = datetime.datetime.strptime(start, "%d/%m/%y %H:%M")
        end = datetime.datetime.strptime(end, "%d/%m/%y %H:%M")
    except ValueError as e:
        print(e)
        flash("Date format should be mm/dd/yy Hour:min:sec")
        return redirect(url_for("classes.index"))

    user = User.query.filter_by(name=current_user.name).first()

    cl = Class(name=name, creatorId=str(user.id),
               studentIds=json.dumps({"id": []}), startTime=start, endTime=end, qr="")

    db.session.add(cl)
    db.session.flush()
    # create the qr code
    url = pyqrcode.create(f"https://qrattn.onrender.com/class/{cl.id}/seek")
    image_as_str = url.png_as_base64_str(scale=5)
    base64_png = f"data:image/png;base64,{image_as_str}"
    cl.qr = base64_png
    class_ids = json.loads(user.class_ids)
    ids = class_ids.get("ids", [])
    if ids is None:
        ids = []
    ids.append(cl.id)
    class_ids["ids"] = ids
    user.class_ids = json.dumps(class_ids)
    db.session.commit()

    return redirect(url_for("main.profile"))
