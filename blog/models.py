from flask_sqlalchemy import SQLAlchemy
import uuid
import datetime

db = SQLAlchemy()


def uuid4():
    return str(uuid.uuid4())


class Page(db.Model):
    __tablename__ = 'pages'
    id = db.Column(db.String, primary_key=True, default=uuid4)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    slug = db.Column(db.String, unique=True, nullable=False)
    is_published = db.Column(db.Boolean, default=True)
    title = db.Column(db.String, nullable=False)
    intro = db.Column(db.String)
    text = db.Column(db.String, nullable=False)

    @staticmethod
    def published():
        return Page.query.filter_by(is_published=True)
