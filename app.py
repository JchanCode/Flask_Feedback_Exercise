from flask import Flask, render_template, redirect, session, flash
from flask_debugtoolbar import DebugToolbarExtension
from models import connect_db, db, User 
from forms import UserForm, LoginForm


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgres:///flask_feedback"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True
app.config["SECRET_KEY"] = "abc123"
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False


connect_db(app)


toolbar = DebugToolbarExtension(app)




@app.route("/")
def home():
    """redirect to register"""
    return redirect("/register")

@app.route("/register", methods=["POST","GET"])
def register():
    """handle register form"""

    form = UserForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        email = form.email.data
        first_name = form.first_name.data
        last_name = form.last_name.data 

        user = User.register(username=username, password=password, email=email, first_name=first_name, last_name=last_name)
        db.session.add(user)
        db.session.commit()
        flash("Welcome! Successfully Created Your Account!","success")

        
        return redirect("/secret")

    return render_template("register.html",form=form)


@app.route("/login", methods=["GET","POST"])
def login():
    """Handle login form"""

    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        user = User.authenticate(username, password)

        if user:
            return redirect("/secret")
        else:
            form.username.errors = ["Invalid username/password"]

    return render_template("login.html",form=form)



@app.route("/secret")
def secret():

    return render_template("secret.html")
