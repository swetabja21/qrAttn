from flask_login import login_user, login_required, logout_user, current_user
from db import db
from models.user import User
from werkzeug.security import generate_password_hash, check_password_hash
from flask import (Blueprint, render_template, abort,
                   redirect, url_for, request, flash)
import json
import requests

auth = Blueprint('auth', __name__, template_folder='templates')


@auth.route('/login')
def login():
    return render_template("login.html")


@auth.route('/login', methods=['POST'])
def login_post():
    # login code goes here
    email = request.form.get('email')
    password = request.form.get('password')
    remember = True if request.form.get('remember') else False

    user = User.query.filter_by(email=email).first()

    # check if the user actually exists
    # take the user-supplied password, hash it,
    # and compare it to the hashed password in the database
    if not user or not check_password_hash(user.password, password):
        flash('Please check your login details and try again.')
        # if the user doesn't exist or password is wrong, reload the page
        return redirect(url_for('auth.login'))

    # if the above check passes,
    # then we know the user has the right credentials
    login_user(user, remember=remember)
    return redirect(url_for('main.profile'))


@auth.route("/signup")
def signup():
    return render_template("signup.html")


@auth.route('/signup', methods=['POST'])
def signup_post():
    # code to validate and add user to database goes here

    name = request.form.get('name')
    email = request.form.get('email')
    role = request.form.get('role')
    password = request.form.get('password')
    cfm = request.form.get('cnfm_password')

    if not (role == 'student' or role == 'professor'):
        flash("Role can only be student or professor")
        return redirect(url_for('auth.signup'))

    if not password == cfm:
        flash("passwords do not match")
        return redirect(url_for('auth.signup'))

    user = User.query.filter_by(email=email).first()

    if user:  # if a user is found, redirect to signup page
        flash("Email already exists")
        return redirect(url_for('auth.signup'))

    # create a new user with the form data.
    # Hash the password so the plaintext version isn't saved.
    new_user = User(
        name=name,
        email=email,
        password=generate_password_hash(password, method='sha256'),
        role=role,
        class_ids=json.dumps({'ids': []}),
        location=json.dumps({'lat': "", 'long': ""}))

    db.session.add(new_user)
    db.session.commit()
    return redirect(url_for('auth.login'))


@auth.route('/locate')
@login_required
def locate():
    client_ip = request.remote_addr
    resp = requests.get(f"http://ip-api.com/json/{client_ip}")
    rjson = resp.json()

    if rjson['status'] == 'fail':
        flash("Invaid IP to take attendance")
        return redirect(url_for("main.profile"))
    lat = rjson['lat']
    lon = rjson['lon']
    u = User.query.filter_by(id=current_user.id).first()
    u.location = json.dumps({ "lat": lat, "lon": lon })
    db.session.commit()

    flash("Location Updated")
    return redirect(url_for("main.profile"))


@ auth.route('/logout')
@ login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))
