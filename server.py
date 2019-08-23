"""Job Ratings."""

from jinja2 import StrictUndefined

from flask import (Flask, render_template, redirect, request, flash, session, url_for)
from flask_debugtoolbar import DebugToolbarExtension

from model import connect_to_db, db, User, Job, Rating

from API import get_api_data

from statistics import mean

import requests
import json



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
    
    session.clear()  
    flash("Successfully Logged Out")

    return redirect("/welcome")



@app.route("/jobs_search")
def job_list_location():
    """Show list of jobs based on location user inputs."""

    location = request.args.get("job location")
    title = request.args.get("job title")

    jobs_query = Job.query        #query for all jobs initially 

    if location:                    #if location is specified, filter for those jobs
        updated_location = f"%{location}%"

        jobs_query = jobs_query.filter(Job.location.like(updated_location))

    if title:                       #if title is specified, filter for those jobs
        updated_title = f"%{title}%"
        jobs_query = jobs_query.filter(Job.title.like(updated_title))

    jobs = jobs_query.all()            #set jobs as all those jobs regardless of inputs 

    if not jobs:
        flash("Sorry, we could not find any jobs that matched your specification")
        return redirect("/")

    return render_template("job_listings.html", jobs=jobs)




@app.route("/job_profile", methods=['GET'])
def job_profile():
    """Show profile of job that user clicks on"""   

    job_id = request.args.get('job_id')  
    job = Job.query.get(job_id) 
    github_job_uid = job.github_job_uid  
 
    # requesting info about the job we clicked on from API
    url = f"https://jobs.github.com/positions/{github_job_uid}.json"

    response = requests.get(url)
    data = response.json()

          
    job_type = data['type']
    company_url = data['company_url']
    description = data['description']
    how_to_apply = data['how_to_apply']
 

    return render_template('job.html', job=job, data=data, job_type=job_type, 
                            company_url=company_url, description=description, 
                            how_to_apply=how_to_apply)



@app.route("/user_profile", methods=['GET'])
def show_user_profile():
    """Show profile of user that's currently logged in."""

    

    user_id = session.get('user_id')
    user = User.query.get(user_id)
 
    
    return render_template('user_profile.html', user=user)


@app.route("/rating", methods=['GET'])
def rating_form():
    """If user has stated in registration that they have experience applying to 
        the job, show them rating form. If not, proceed to job profile. 
    """

    job_id = request.args.get('job_id')
    job = Job.query.get(job_id)
    return render_template("rating_form.html", job=job)


#after user submits rating for a job listing, they 're brought to this route
@app.route("/rating", methods=['POST'])
def record_rating():
    """Allow user to submit a rating for a job listing"""


    #getting job id from the form user submits 
    job_id = request.form['job_id']
      
    # what the user rated the job  
    score_value = request.form['option']

    # first confirm if they are logged in --> user_id in session 
    user_id = session.get('user_id')
    
     
    if not user_id:
        flash("You're not logged in.")
        return redirect("/login")
    else:
      
        #doing a joined load so that only 1 query is sent to server 
        user = User.query.options(db.joinedload('ratings')).get(user_id)
        
        job = Job.query.get(job_id)

        #create a new list that has all the job objects that user has rated already
        #user.ratings = all the ratings that specific user has rated 
        jobs_rated = [rating.job for rating in user.ratings]
        print(user.ratings)
       
        if job in jobs_rated:
            Raise("You've already rated this job posting!!")

        else:
            # if user hasn't rated the job listing yet, allow them to submit a rating
            # -->don't need to pass in user_id or job_id b/c of unique constraints
            rating = Rating(rating=int(score_value), job=job)     
            user.ratings.append(rating)   #automatically appends new rating into user.ratings list and into DB 
            flash("Thank you, your rating was added!")
    

    db.session.commit()

    #redirecting back to specific job's profile page 
    return redirect(f"/profile?job_id={job_id}")
            
 

@app.route("/average", methods=['GET'])
def return_average_rating():
    """Returns the average rating for a specific job posting"""

    job_id = request.args.get('job_id')
    rating = Job.query.options(db.joinedload('ratings')).get(job_id)    
    job = Job.query.get(job_id)      #get the job_id of the specific job posting 
                 #returns list of rating objects of the job (all ratings of the job)
    
    ratings_list = []
    for each_rating in job.ratings: 
        ratings_list.append(each_rating.rating)
        average = round(mean(ratings_list), 1)
    if average is None:
        return "No average rating available!"
    else:
        return str(average)

    


@app.route("/company_avg", methods=['GET'])
def return_company_average():
    """Returns the average rating for a Company via multiple job postings and ratings."""
    

    job_id = request.args.get('job_id')
    job = Job.query.get(job_id)
    # company = Job.query.filter(Job.company == f'{job.company}').all()   #list of all job objects that have 'company'


    company = db.session.query(Rating.rating).join(Job, Job.job_id == Rating.job_id).filter(Job.company == f'{job.company}').all()

    ratings_list = []
    for each_tuple in company:
        ratings_list.append(each_tuple[0])
    return str(mean(ratings_list))

    






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
