from flask_login import UserMixin

from .base import Base
from db import db


class User(UserMixin, Base):
    name = db.Column(db.String(128), nullable=False)
    email = db.Column(db.String(128), nullable=False, unique=True)
    password = db.Column(db.String(100), nullable=False)
    class_ids = db.Column(db.Text)
    role = db.Column(db.String(10), nullable=False)  # professor | student
    location = db.Column(db.Text, nullable=False)

    def __init__(self, name, email, password, role, class_ids, location):
        self.name = name
        self.email = email
        self.class_ids = class_ids
        self.password = password
        self.role = role
        self.location = location

    def update(self, name, email, passowrd, role, class_ids, location):
        self.name = name
        self.role = role
        self.email = email
        self.class_ids = class_ids
        self.password = passowrd
        self.location = location

    def __repr__(self):
        return self.name
