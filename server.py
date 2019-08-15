"""Job Ratings."""

from jinja2 import StrictUndefined

from flask import (Flask, render_template, redirect, request, flash, session)
from flask_debugtoolbar import DebugToolbarExtension

from model import connect_to_db, db, User, Job, Rating


app = Flask(__name__)

# Required to use Flask sessions and the debug toolbar
app.secret_key = "Yeah you wish you knew"

app.jinja_env.undefined = StrictUndefined


@app.route('/')
def index():
    """Homepage that renders the search page"""

    return render_template("index.html")

@app.route('/welcome')
def welcome():
    """Page where user can sign in or sign up"""

    return render_template("welcome_page.html")

@app.route('/register', methods=['GET'])
def register_form():
    """Show form for user signup."""

    return render_template("register_form.html")


@app.route('/register', methods=['POST'])
def register_process():
    """Process registration."""

    # Get form variables
    fname = request.form["fname"]
    lname = request.form["lname"]
    email = request.form["email"]
    password = request.form["password"]
    

    new_user = User(fname=fname, lname=lname, email=email, password=password)

    db.session.add(new_user)
    db.session.commit()

    flash(f"User {email} added.")
    return redirect("/")


@app.route('/login')
def login_form():
    """Show login form."""

    return render_template("login_form.html")


@app.route('/login', methods=['POST'])
def login_process():
    """Process login."""

    # Get form variables
    email = request.form["email"]
    password = request.form["password"]

    user = User.query.filter_by(email=email).first()    #querying into db for email

    if not user:
        flash("Sorry, we don't recognize your email")
        return redirect("/login")

    if user.password != password:
        flash("Incorrect password")
        return redirect("/login")

    session["user_id"] = user.user_id        #save the user_id in session dict.

    flash("Logged in")
    return redirect("/")


@app.route('/logout')
def logout():
    """Log out."""

    print(session)          # to see if user_id is actually being deleted 
    del session["user_id"]  
    print(session)            #deleting the user_id from session dict.
    flash("Successfully Logged Out")
    return redirect("/welcome")


@app.route("/jobs")
def movie_list():
    """Show list of jobs based on user input."""

    title = request.form["job title"]

    jobs = Job.query.filter_by(title=title).all()
    return render_template("job_listings.html", )



@app.route('/job_listings')
def display_jobs():
    """Page that displays all jobs specific to User's inputs on search page"""

    return render_template("job_listings.html")







if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the
    # point that we invoke the DebugToolbarExtension
    app.debug = True
    # make sure templates, etc. are not cached in debug mode
    app.jinja_env.auto_reload = app.debug
    app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run(port=5000, host='0.0.0.0')
