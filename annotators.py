from flask import flash, redirect, url_for
from flask_login import current_user
from functools import wraps


def must_be_professor(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        if current_user.role != "professor":
            flash("You are not authorized to access this route.")
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorator
