from flask import Blueprint, render_template
from flask_login import login_required, current_user
from models.user import User
from models.clas import Class
import json

index_routes = Blueprint('main', __name__, template_folder='templates')


@index_routes.route('/')
def index():
    return render_template("index.html")


@index_routes.route("/profile")
@login_required
def profile():
    classes = []

    print(current_user.is_authenticated)

    if current_user.role == "professor":
        classes = Class.query.filter_by(creatorId=str(current_user.id)).all()
    else:
        user = User.query.filter_by(email=current_user.email).first()
        print(user)
        class_ids = json.loads(user.class_ids).get('ids', [])
        print(class_ids)
        if class_ids is not None:
            for id in class_ids:
                classes.append(Class.query.filter_by(id=id).first())
    return render_template("profile.html", classes=classes)
