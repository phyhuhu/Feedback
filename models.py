"""Models for Blogly."""
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()
db=SQLAlchemy()

def connect_db(app):
    db.app=app
    db.init_app(app)

class Users(db.Model):
    __tablename__='users'

    username=db.Column(db.String(20), primary_key=True, unique=True, nullable=False)
    password=db.Column(db.String, nullable=False)
    email=db.Column(db.String(50), nullable=False)
    first_name=db.Column(db.String(30), nullable=False)
    last_name=db.Column(db.String(30), nullable=False)

    feedbacks = db.relationship("Feedbacks", backref="users", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Users_inf: {self.username} {self.first_name} {self.last_name}>"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    # register
    @classmethod
    def register(cls, username, password, checkpassword, first_name, last_name, email):
        hashed = bcrypt.generate_password_hash(password)
        hashed_utf8 = hashed.decode("utf8")
        print(password, checkpassword)

        if password==checkpassword:
            user=cls(username=username,
                    password=hashed_utf8,
                    first_name=first_name,
                    last_name=last_name,
                    email=email
                    )

            return user
        else:
            return False

    # authenticate
    @classmethod
    def authenticate(cls, username, password):
        user = Users.query.filter_by(username=username).first()

        if user and bcrypt.check_password_hash(user.password, password):
            return user
        else:
            return False

class Feedbacks(db.Model):
    __tablename__='feedbacks'

    id=db.Column(db.Integer, primary_key=True, autoincrement=True)
    title=db.Column(db.String(100), nullable=False)
    content=db.Column(db.String, nullable=False)
    username_id=db.Column(db.String(20), db.ForeignKey('users.username'), nullable=False)

    def __repr__(self):
        return f"<Feedbacks: {self.id} {self.title}>"