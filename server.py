"""Job Ratings."""

from jinja2 import StrictUndefined

from flask import (Flask, render_template, redirect, request, flash, session)
from flask_debugtoolbar import DebugToolbarExtension

from model import connect_to_db, db, User, Job, Rating


app = Flask(__name__)

# Required to use Flask sessions and the debug toolbar
app.secret_key = "YeahYouWishYouKnew"

app.jinja_env.undefined = StrictUndefined


@app.route('/')
def index():
    """Homepage that renders the search page"""

    return render_template("index.html")

@app.route('/welcome')
def welcome():
    """Page where user can sign in or sign up"""

    return render_template("welcome_page.html")

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
    return redirect("/welcome")


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

    user = User.query.filter_by(email=email).first() #querying into db for email

    if not user:
        flash("Sorry, we don't recognize your email")
        return redirect("/login")

    if user.password != password:
        flash("Incorrect password")
        return redirect("/login")

    session["user_id"] = user.user_id      #save the user_id in session dict.

    print(session)

    flash("Logged in")
    return redirect("/")


@app.route('/logout')
def logout():
    """Log out user."""

    print(session)          # to see if user_id is actually being deleted 
    session.clear()  
    print(session)            #deleting the user_id from session dict.
    flash("Successfully Logged Out")
    return redirect("/welcome")


@app.route("/jobs_title")
def job_list_title():
    """Show list of jobs based on title user inputs."""

    # first starting with specifying the job title 

    title = request.args.get("job title")

    #returns list of job objects 
    updated_title = f"%{title}%"
    jobs = Job.query.filter(Job.title.like(updated_title)).all()
    return render_template("job_listings.html", jobs=jobs)

@app.route("/jobs_location")
def job_list_location():
    """Show list of jobs based on location user inputs."""

    location = request.args.get("job location")
    updated_location = f"%{location}%"

    jobs = Job.query.filter(Job.location.like(updated_location)).all()
    return render_template("job_listings.html", jobs=jobs)


# <!!!!!!!------WORK ON THIS AFTER YOU FINISH RATING THE JOB----------!!!!!!!!>
@app.route("/jobs_both")
def job_list():
    """Show list of jobs based on location and title user inputs."""

    both = request.args.get("both")
    updated_both = f'%{both}%'

  
#<---------------------------------------------------------------------------->


@app.route("/profile")
def job_profile():
    """Show profile of job that user clicks on"""

    job_id = request.args.get('job_id')
    job = Job.query.get(job_id)
    
    return render_template('job.html', job=job)


@app.route("/rating", methods=['GET'])
def rating_form():
    """If user has stated in registration that they have experience applying to 
        the job, show them rating form. If not, proceed to job profile. 
    """
    return render_template("rating_form.html")


#RATING FORM -- APPLYED OPTION ROUTE
@app.route("/submit", methods=['POST'])
def score_job_listing_1():
    """Allow user to submit a rating for a job listing"""

    job_id = request.args.get('job_id')
  
    # what the user checked 
    score_value = request.form["option"]

    # first confirm if they are logged in.user_id in session 
    user_id = session.get('user_id')
 

    if not user_id:
        raise Exception("You're not logged in.")
        return redirect("/login")
    if user_id:
        #checking to see if user already rated this job 
        rating = Rating.query.filter_by(user_id=user_id, job_id=job_id).first()
        print(rating)
        #if there is a rating already there, don't allow user to rate that job again
        if rating:
            flash("You've already rated this job listing")
        else: 
            rating_value = Rating(user_id=user_id, job_id=job_id, rating=int(score_value))
            print(rating_value)
            flash("Thank you, your rating was added!")

        db.session.add(rating_value)


    db.session.commit()

    return redirect("/profile")
 








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
