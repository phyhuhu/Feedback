"""Blogly application."""

from flask import Flask, request, render_template, redirect, session, flash, make_response, jsonify, url_for
from flask_debugtoolbar import DebugToolbarExtension
from werkzeug.exceptions import Unauthorized

from models import db, connect_db, Users, Feedbacks

from forms import RegisterForm, LoginForm, FeedbackForm

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret'
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///feedbacks'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False

connect_db(app)
db.create_all()

@app.route('/')
def homepage():
    return redirect('/register')

@app.route('/login', methods=['GET','POST'])
def login():
    if 'username' in session:
        username=session['username']
        return redirect(f'/users/{username}')

    form=LoginForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        user = Users.authenticate(username, password)

        if user:
            session['username'] = user.username
            return redirect(f'/users/{user.username}')
        else:
            form.username.errors = ["Invalid username/password."]
            kind='Login'
            return render_template("users/login_register.html", form=form, kind=kind)

    else:
        kind='Login'
        return render_template("users/login_register.html", form=form, kind=kind)

@app.route('/register', methods=['GET','POST'])
def register():
    if 'username' in session:
        username=session['username']
        return redirect(f'/users/{username}')

    form=RegisterForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        checkpassword = form.checkpassword.data
        first_name = form.first_name.data
        last_name = form.last_name.data
        email = form.email.data

        user = Users.register(username, password, checkpassword, first_name, last_name, email)

        if user:
            db.session.add(user)
            db.session.commit()

            session['username'] = user.username

            return redirect(f'/users/{user.username}')
        else:
            form.checkpassword.errors = ["Please check password."]

            kind='Sign Up'
            return render_template("users/login_register.html", form=form, kind=kind)

    else:
        kind='Sign Up'
        return render_template("users/login_register.html", form=form, kind=kind)

@app.route("/logout")
def logout():
    session.pop("username")
    return redirect("/login")

@app.route("/users/<string:username>")
def show(username):
    if 'username' in session or username != session['username']:
        user = Users.query.get(username)
        return render_template("users/show.html", user=user)
    else:
        # raise Unauthorized()
        return render_template('404.html'), 404

@app.route("/users/<username>/delete", methods=["POST"])
def remove_user(username):
    if "username" not in session or username != session['username']:
        # raise Unauthorized()
        return render_template('404.html'), 404

    user = Users.query.get(username)
    db.session.delete(user)
    db.session.commit()
    session.pop("username")

    return redirect("/")

@app.route("/users/<username>/feedback/add", methods=["GET", "POST"])
def add_feedback(username):
    if "username" not in session or username != session['username']:
        # raise Unauthorized()
        return render_template('404.html'), 404

    form = FeedbackForm()

    if form.validate_on_submit():
        title=form.title.data
        content=form.content.data

        feedback=Feedbacks(title=title,content=content,username_id=username)

        db.session.add(feedback)
        db.session.commit()

        return redirect(f"/users/{feedback.username_id}")

    else:

        return render_template("feedback/add.html", form=form, username=username)

@app.route("/feedback/<int:feedback_id>/update", methods=["GET", "POST"])
def update_feedback(feedback_id):
    feedback = Feedbacks.query.get(feedback_id)

    if "username" not in session or feedback.username_id != session['username']:
        # raise Unauthorized()
        return render_template('404.html'), 404

    form = FeedbackForm(obj=feedback)

    if form.validate_on_submit():
        feedback.title = form.title.data
        feedback.content = form.content.data

        db.session.commit()

        return redirect(f"/users/{feedback.username_id}")

    return render_template("/feedback/edit.html", form=form, feedback=feedback)

@app.route("/feedback/<int:feedback_id>/delete", methods=["POST"])
def delete_feedback(feedback_id):
    feedback = Feedbacks.query.get(feedback_id)

    if "username" not in session or feedback.username_id != session['username']:
        # raise Unauthorized()
        return render_template('404.html'), 404

    db.session.delete(feedback)
    db.session.commit()

    return redirect(f"/users/{feedback.username_id}")