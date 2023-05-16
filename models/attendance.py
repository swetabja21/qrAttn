from .base import Base
from db import db
from .user import User

from datetime import datetime


class Attendance(Base):
    professor_id = db.Column(db.Text, nullable=False)
    student_id = db.Column(db.Text, nullable=False)
    class_id = db.Column(db.Text, nullable=False)
    verified = db.Column(db.Boolean, nullable=False, default=False)
    date = db.Column(db.Date, nullable=False,
                     default=datetime.today().date())

    def __init__(self, pid, sid, cid, verified):
        self.professor_id = pid
        self.student_id = sid
        self.class_id = cid
        self.verified = verified

    def update(self, pid, sid, cid, verified):
        self.professor_id = pid
        self.student_id = sid
        self.class_id = cid
        self.verified = verified

    def __repr__(self):
        return "signed" if self.verified else "unsigned"

    def get_attendance_of_class_on_date(cid, date):
        entries = Attendance.query.filter(
            Attendance.class_id == cid,
            Attendance.date == date).all()
        print("entries", entries)
        students_present = []

        for entry in entries:
            students_present.append(entry.student_id)

        return students_present
