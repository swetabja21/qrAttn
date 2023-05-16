from .base import Base
from db import db


class Class(Base):
    name = db.Column(db.String(128), nullable=False)
    creatorId = db.Column(db.Text, nullable=False)
    studentIds = db.Column(db.Text, nullable=False)
    startTime = db.Column(db.DateTime(timezone=True), nullable=False)
    endTime = db.Column(db.DateTime(timezone=True), nullable=False)
    qr = db.Column(db.Text)

    def __init__(self, name, creatorId, studentIds, startTime, endTime, qr):
        self.name = name
        self.creatorId = creatorId
        self.studentIds = studentIds
        self.startTime = startTime
        self.endTime = endTime
        self.qr = qr

    def update(self, name, creatorId, studentIds, startTime, endTime, qr):
        self.name = name
        self.creatorId = creatorId
        self.studentIds = studentIds
        self.startTime = startTime
        self.endTime = endTime
        self.qr = qr

    def __repr__(self):
        return self.name
