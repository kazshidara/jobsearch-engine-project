from jinja2 import StrictUndefined

from flask import (Flask, render_template, redirect, request, flash, session, url_for, jsonify)
from flask_debugtoolbar import DebugToolbarExtension

from model import connect_to_db, db, User, Job, Rating, Savings

from API import get_api_data

from statistics import mean
from datetime import datetime, date

import requests
import json
from functions import days_from_date


app = Flask(__name__)

# Required to use Flask sessions and the debug toolbar
app.secret_key = "YeahYouWishYouKnew"

app.jinja_env.undefined = StrictUndefined


################################################################################
################################################################################


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
    
    email_check = User.query.filter_by(email=email).first()
    password_check = User.query.filter_by(password=password).first()

    if email_check:
        
        flash("The email you entered is already registered, please sign in or enter a different email")
    
    elif password_check:
        
        flash("Please register with a different password")
    
    else:
        new_user = User(fname=fname, lname=lname, email=email, password=password)

        db.session.add(new_user)
        db.session.commit()

        flash(f"User {email} added.")

    return redirect("/login")


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
    current_date = datetime.today()
    
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

    return render_template("job_listings.html", jobs=jobs, current_date=current_date)


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

    num_days = days_from_date(job.released_at)

    return render_template('job.html', job=job, data=data, job_type=job_type, 
                            company_url=company_url, description=description, 
                            how_to_apply=how_to_apply,
                            num_days=num_days)


@app.route("/user_profile", methods=['GET'])
def show_user_profile():
    """Show profile of user that's currently logged in."""

    user_id = session.get('user_id')
    user = User.query.get(user_id)
   
    return render_template('user_profile.html', user=user)


@app.route("/rating", methods=['GET'])
def show_rating_form():
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
    job_id = request.args.get('job_id')
      
    # first confirm if they are logged in --> user_id in session 
    user_id = session.get('user_id')
    
    if not user_id:
        flash("You're not logged in. Please login to submit a rating!")
        return redirect("/login")

    else:
        # what the user rated the job  
        score_value = request.form['rating_val']
        print("SCOREEE VALUEEEE", score_value)
        
        #doing a joined load so that only 1 query is sent to server 
        user = User.query.options(db.joinedload('ratings')).get(user_id)
        
        job = Job.query.get(job_id)
    
        #create a new list that has all the job objects that user has rated already
        #user.ratings = all the ratings that specific user has rated 
        jobs_rated = [rating.job for rating in user.ratings]
       
        if job in jobs_rated:
            
            return "You've already rated this job"
        
        else:
            # if user hasn't rated the job listing yet, allow them to submit a rating
            # -->don't need to pass in user_id or job_id b/c of unique constraints
            rating = Rating(rating=int(score_value), job=job)     
            user.ratings.append(rating)   #automatically appends new rating into user.ratings list and into DB 
            
            db.session.commit()

            return "Thank you, your rating has been recorded!"
            

@app.route("/average", methods=['GET'])
def return_average_rating():
    """Returns the average rating for a specific job posting"""

    job_id = request.args.get('job_id')
    rating = Job.query.options(db.joinedload('ratings')).get(job_id)    
    job = Job.query.get(job_id)      #get the job_id of the specific job posting 
                 #returns list of rating objects of the job (all ratings of the job)
    
    ratings_list = []

    if job.ratings:
        for each_rating in job.ratings: 
            ratings_list.append(each_rating.rating)
        average = round(mean(ratings_list), 1)
        print("AVERAGEEEE", average)

        if 0 <= average < 1:
            response = "On average, applicants who applied to this job didn't hear back"
        elif 1 <= average < 2:
            response = "On average, applicants who applied to this job heard back from a recruiter"
        elif 2 <= average < 3:
            response = "On average, applicants who applied to this job received a phone screen interview"
        elif 3 <= average < 4:
            response = "On average, applicants who applied to this job got through to the onsite interview"
        else:
            response = "On average, applicants who applied to this job received a job offer!"       
        return response
    else:
        return "No ratings on this job posting yet!"


@app.route("/company_avg", methods=['GET'])
def return_company_average():
    """Returns the average rating for a Company via multiple job postings and ratings."""
    
    job_id = request.args.get('job_id')
    job = Job.query.get(job_id)

    # add where clause to filter results matching the job id we care about
    #  add another where clause where the rating is not null
    #  additionally we can group the results by rating (GROUP BY rating)
    #. and finally we want the average (SELECT AVG(rating))
    #. | rating |
    #. | ------ |
    #. |  3.5.  |
    company = db.session.query(Rating.rating).join(Job, Job.job_id == Rating.job_id).filter(Job.company == f'{job.company}').all()
    
    ratings_list = []
    
    for each_tuple in company:
        ratings_list.append(each_tuple[0])
     
    
    if len(ratings_list) == 0:
        return "No information on this Company yet!"

    else:
        avg_company_rating = mean(ratings_list)

        if 0 <= avg_company_rating < 1:
            response = "On average, applicants who applied to this company didn't hear back"
        elif 1 <= avg_company_rating < 2:
            response = "On average, applicants who applied to this company heard back from a recruiter"
        elif 2 <= avg_company_rating < 3:
            response = "On average, applicants who applied to this company received a phone screen interview"
        elif 3 <= avg_company_rating < 4:
            response = "On average, applicants who applied to this company got through to the onsite interview"
        else:
            response = "On average, applicants who applied to this company received a job offer!"
        
        return response


@app.route("/user-ratings.json")
def return_user_ratings():
    """Returns all the ratings that a user made to display on a chart."""
    
    user_id = session.get('user_id')

    user = User.query.options(db.joinedload('ratings')).get(user_id)
    
    job_object = db.session.query(Job, Rating).join(Rating, Job.job_id == Rating.job_id).filter(Rating.user_id==f'{user_id}').all()
    print("ALL JOB OBJECTS FOR USERRRRRR", job_object)
    
    # Each point in the graph will represent:
    #  company name
    #  job title
    #  location

    user_ratings = []

    for job in job_object:    
        print("Job in job list: ", job)

        user_ratings.append({
            "title" : job[0].title,
            "company" : job[0].company,
            "location" : job[0].location,
            "rating" : job[1].rating
            })

    print("USER RATINGS:", user_ratings)



        #create a new list that has all the job objects that user has rated already
        #user.ratings = all the ratings that specific user has rated 
    jobs_rated = user.ratings
    
    ratings_list = []
    
    for rating in jobs_rated:
        ratings_list.append(rating.rating)
    
    # # x_axis has the number of ratings the user has made, counting the number using indices
    x_axis = []
    for i,rating in enumerate(user_ratings):
        x_axis.append(i+1)


    data_dict = {
                "data_points" : user_ratings,
                "labels": x_axis,
                "datasets": [
                    {
                        "data": ratings_list,
                        "backgroundColor": [
                            "#99d8c9"],
                        "hoverBackgroundColor": [
                            "#FF6384" for color in x_axis]
                    }]
            }
 
    return jsonify(data_dict)   #data_dict is what gets passed into JS function(data)


@app.route("/moreCompanyInfo", methods=['GET'])
def show_company_profile():
    """Renders company profile page."""

    job_id = request.args.get('job_id') 
    job = Job.query.get(job_id)

    return render_template("company_profile.html", job=job)



@app.route("/company_ratings.json")
def return_company_ratings():
    """Returns all the ratings that all users for a certain COMPANY made to display on a chart."""
    
    job_id = int(request.args.get('job_id'))
    
    
    job = Job.query.get(job_id)
    print("JOB!!!!!", job)

    company = db.session.query(Rating).join(Job, Job.job_id == Rating.job_id).filter(Job.company == f'{job.company}').all()
    print("COMPANYYYY - Rating objects of all companies that have been rated", company)

    company_ratings = []
    for each in company:
        company_ratings.append(each.rating)
    print(company_ratings)

    company_dict = {0: 0,
                    1: 0,
                    2: 0,
                    3: 0,
                    4: 0}

    for each in company:
        company_dict[each.rating] += 1

    number_of_ratings = []

    for key, value in company_dict.items():
        number_of_ratings.append(value)


    data_dict = {
                # "data_points" : company_ratings,     
                "labels": ["Received Application","Recruiter Responded","Phone Screen Administered",
                            "Onsite Interview Administered","Job Offered"],
                "datasets": [
                    {
                        "data": number_of_ratings,
                        "backgroundColor": ["#3e95cd", "#8e5ea2","#3cba9f","#e8c3b9","#c45850"],
                        
                    }]
            }

    return jsonify(data_dict)

    
@app.route("/saved", methods=['GET','POST'])
def return_saved_jobs():
    """Returns all the jobs that a user saved."""

    user_id = session.get('user_id')

    if not user_id:
        flash("Please sign in first to save this job")
        return redirect("/login")

    else:

        user = User.query.options(db.joinedload('saved_jobs')).get(user_id)
           
        job_id = request.args.get('job_id')       
        job = Job.query.get(job_id)

        if job in user.saved_jobs:
            flash("You've already saved this job")
            return redirect(f"/job_profile?job_id={job.job_id}")

        else:
            save_job = Savings(user_id=user_id, job_id=job_id)
            print(save_job)

            db.session.add(save_job)
            db.session.commit()

            flash("This job has been saved to your profile!") 

    return redirect(f"/job_profile?job_id={job.job_id}")


@app.route("/show-saved", methods=['GET'])
def show_saved_jobs():
    """Shows a list of all jobs saved by user."""

    user_id = session.get('user_id')
    user = User.query.options(db.joinedload('saved_jobs')).get(user_id)
    saved_jobs = user.saved_jobs
    current_date = datetime.today()

    return render_template("saved.html", saved_jobs=saved_jobs, current_date=current_date)
    

@app.route("/user-events")
def show_events():
    """Calling Eventbrite API and showing a list of Eventbrite events happening based on User's average rating"""

    user_location = "San Francisco"

    payload = {'token' : 'W5TEINASBAG56UPMVLKI'}
    
    user_id = session.get('user_id')

    user = User.query.options(db.joinedload('ratings')).get(user_id)
        

        #create a new list that has all the job objects that user has rated already
        #user.ratings = all the ratings that specific user has rated 
    jobs_rated = user.ratings
    rating_list = []
    for rating in jobs_rated:
        rating_list.append(rating.rating)
    print("USER AVGGGGG")
    print(mean(rating_list))
    
    #networking and career events (Good for user average's that are between 0 and 1)
    if mean(rating_list) <= 1:

        url = f"https://www.eventbriteapi.com/v3/events/search/?q=software+engineering+networking&sort_by=date&location.address={user_location}&location.within=10mi&categories=101%2C102&subcategories=1004%2C2004%2C1010"
    
    # class events (Good for user averages that are between 1 and 3 - brush up on technical knowledge)
    elif 1 < mean(rating_list) <= 3:

        url = f"https://www.eventbriteapi.com/v3/events/search/?q=software+engineering+class&sort_by=date&location.address={user_location}&location.within=10mi&categories=101%2C102&subcategories=1001%2C2004%2C1004%2C1010"

    #conferences and talk events (Good for user averages that are above 3)
    elif mean(rating_list) > 3:

        url = f"https://www.eventbriteapi.com/v3/events/search/?q=software+engineering+conference&sort_by=date&location.address={user_location}&location.within=10mi&categories=101%2C102&subcategories=1001%2C2004%2C1009"
    
    
    response = requests.get(url, params=payload)

    events = response.json()

    new_dict = {}

    for event in events['events']:

        new_dict[event['organization_id']] = event['name']['text'], event['summary'],event['url'], event['logo']['url']
    
    return render_template("recommended_events.html", new_dict=new_dict)



################################################################################
################################################################################


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
