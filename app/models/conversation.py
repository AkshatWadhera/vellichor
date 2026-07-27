from app import db
from datetime import datetime

class Conversation(db.Model):
    __tablename__ = "conversations"

    id = db.Column(db.Integer, primary_key=True)

    title = db.Column(db.String(200), nullable=False)

    created_at = db.Column(
        db.DateTime,
        default = datetime.utcnow,
        nullable=False
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    pdf = db.relationship(
        "PDF",
        backref="conversation",
        uselist=False,
        cascade="all, delete-orphan"
    )

    messages = db.relationship(
        "Message",
        backref="conversation",
        lazy="select",
        cascade="all, delete-orphan"
    )