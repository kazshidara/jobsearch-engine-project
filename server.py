"""Job Ratings."""

from jinja2 import StrictUndefined

from flask import (Flask, render_template, redirect, request, flash, session)
from flask_debugtoolbar import DebugToolbarExtension

from model import connect_to_db, db, User, Job, Rating


app = Flask(__name__)

# Required to use Flask sessions and the debug toolbar
app.secret_key = "ABC"

app.jinja_env.undefined = StrictUndefined


@app.route('/')
def index():
    """Homepage that renders the search page"""

    return render_template("index.html")

@app.route('/register')
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


@app.route('/login', methods=['GET'])
def login_form():
    """Show login form."""

    return render_template("login_form.html")


@app.route('/login', methods=['POST'])
def login_process():
    """Process login."""

    # Get form variables
    email = request.form["email"]
    password = request.form["password"]

    user = User.query.filter_by(email=email).first()

    if not user:
        flash("No such user")
        return redirect("/login")

    if user.password != password:
        flash("Incorrect password")
        return redirect("/login")

    session["user_id"] = user.user_id

    flash("Logged in")
    return redirect(f"/users/{user.user_id}")


@app.route('/logout')
def logout():
    """Log out."""

    del session["user_id"]
    flash("Logged Out.")
    return redirect("/")


@app.route("/movies")
def movie_list():
    """Show list of movies."""

    movies = Movie.query.order_by('title').all()
    return render_template("movie_list.html", movies=movies)



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
