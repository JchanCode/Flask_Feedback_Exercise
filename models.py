from enum import unique
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from sqlalchemy.orm import backref

db = SQLAlchemy()

bcrypt = Bcrypt()


def connect_db(app):
    """Connect to database."""

    db.app = app
    db.init_app(app)




class User(db.Model):
    __tablename__ = "users"

    username = db.Column(db.String(20), primary_key=True, unique=True)
    password = db.Column(db.Text, nullable=False)
    email = db.Column(db.String(50), nullable=False, unique=True)
    first_name = db.Column(db.String(30), nullable=False)
    last_name = db.Column(db.String(30), nullable=False)
    is_admin = db.Column(db.Boolean, nullable=False, default=False)
    feedbacks = db.relationship("Feedback", backref="users", cascade="all, delete-orphan")

    @classmethod
    def register(cls, username, password, email, first_name, last_name, is_admin=False):
        """register user"""

        hashed = bcrypt.generate_password_hash(password)
        hashed_utf8 = hashed.decode("utf-8")

        return cls(username=username, password=hashed_utf8, email=email, first_name=first_name, last_name=last_name, is_admin=is_admin)


    @classmethod
    def authenticate(cls, username, password):
        """authenticate user"""

        authenticated_user = User.query.filter_by(username=username).first()
     
        if authenticated_user and bcrypt.check_password_hash(authenticated_user.password, password):
            return authenticated_user
        else:
            return False


class Feedback(db.Model):
    __tablename__ = "feedbacks"

    id = db.Column(db.Integer, primary_key=True,
                   unique=True, autoincrement=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    username = db.Column(db.String, db.ForeignKey("users.username", ondelete="CASCADE"))

    @classmethod
    def submit(cls, title, content, username):
        """create new feedback"""

        return cls(title=title, content=content, username=username)