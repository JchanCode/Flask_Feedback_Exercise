from flask import Flask, render_template, redirect, session, flash
from flask_debugtoolbar import DebugToolbarExtension
from models import connect_db, db, User, Feedback
from forms import UserForm, LoginForm, FeedbackForm


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgres:///flask_feedback"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True
app.config["SECRET_KEY"] = "abc123"
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False


connect_db(app)


toolbar = DebugToolbarExtension(app)










"""

                                Login / Logout Route

"""


@app.route("/")
def home():
    """redirect to register"""

    if "username" in session:
        return redirect(f"/users/{session['username']}")

    return redirect("/register")


@app.route("/login", methods=["GET","POST"])
def login():
    """Handle login form"""

    if "username" in session:
        flash("You already login")
        return redirect(f"/users/{session['username']}")

    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        
        user = User.authenticate(username, password)

        if user:
            session["username"] = user.username
            session["is_admin"] = user.is_admin
            return redirect(f"/users/{user.username}")
        else:
            form.username.errors = ["Invalid username/password"]
    return render_template("login.html",form=form)


@app.route("/logout")
def logout():
    """logout user and pop session"""

    session.pop("username")
    flash("You've logged out!", "primary")
    return redirect("/")


"""

                                Register / User Routes

"""


@app.route("/register", methods=["POST", "GET"])
def register():
    """handle register form"""

    if "username" in session:
        flash("please logout before registering a new account")
        return redirect(f"/users/{session['username']}")

    form = UserForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        email = form.email.data
        first_name = form.first_name.data
        last_name = form.last_name.data

        user = User.register(username=username, password=password,
                             email=email, first_name=first_name, last_name=last_name)
        db.session.add(user)
        db.session.commit()
        flash("Welcome! Successfully Created Your Account!", "success")

        session["username"] = user.username
        return redirect(f"/users/{user.username}")

    return render_template("register.html", form=form)


@app.route("/users/<username>")
def secret(username):
    """Check session for username. Render User page"""

    if "username" not in session:

        flash("Please Log In", "danger")
        return redirect("/login")

    if session["is_admin"]:
        admin = User.query.filter_by(username=username).first()
        all_users = User.query.all()
        all_feedbacks = Feedback.query.all()
        return render_template("admin.html",users=all_users,feedbacks=all_feedbacks,admin=admin)

    user = User.query.filter_by(username=username).first()
    feedbacks = Feedback.query.filter_by(username=username).all()
    return render_template("secret.html", user=user,feedbacks=feedbacks)


@app.route("/users/<username>/feedback/add", methods=["GET","POST"])
def feedback_add(username):
    """Display form for user to add a feedback"""

    if "username" not in session:
        flash("You Need To Be Logged In for this","danger")
        return redirect("/login")

    form = FeedbackForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=username).first()

        title = form.title.data
        content = form.content.data
        username = user.username

        new_post = Feedback.submit(title, content, username)
        db.session.add(new_post)
        db.session.commit()

        flash("Post Added!","info")
        return redirect(f"/users/{user.username}")
        
    return render_template("feedback_add.html", form=form)


@app.route("/users/<username>/delete", methods=["POST"])
def user_delete(username):
    """Delete user and user's post"""

    if "username" not in session:
        flash("You Need To Be Logged In For This", "danger")
        return redirect("/login")

    user = User.query.filter_by(username=username).first()
    db.session.delete(user)
    db.session.commit()
    flash("User successfully deleted","danger")
    return redirect("/")
"""

                                Feedback Routes

"""
@app.route("/feedback/<feedback_id>/update", methods=["POST","GET"])
def feedback_edit(feedback_id):
    """Edit feedback page"""

    if "username" not in session:
        flash("You Really Need To Be Logged In For This","danger")
        return redirect("/login")

    form = FeedbackForm()
    feedback = Feedback.query.get_or_404(feedback_id)

    if feedback.username == session["username"]:
        if form.validate_on_submit():
            feedback.title = form.title.data
            feedback.content = form.content.data
            db.session.commit()
            flash("Feedback Edited","success")
            return redirect(f"/users/{feedback.username}")
        
        
        return render_template("feedback_edit.html",form=form,feedback=feedback)

    flash("You don't have permission to edit this post","warning")
    return redirect("/")


@app.route("/feedback/<feedback_id>/delete",methods=["POST"])
def feedback_delete(feedback_id):
    """Delete selected feedback"""

    if "username" not in session:
        flash("You Need To Be Logged In For This","warning")
        return redirect("/login")
    
    feedback = Feedback.query.get_or_404(feedback_id)

    if feedback.username == session["username"]:
        db.session.delete(feedback)
        db.session.commit()
        flash("Feedback Deleted",'danger')
        return redirect(f"/users/{feedback.username}")
            

"""

                                Error Pages

"""


@app.errorhandler(404)
def page_not_found(e):
    """404 page"""
    return render_template("404.html"), 404
