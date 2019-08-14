"""Utility file to seed ratings database from MovieLens data in seed_data/"""

import datetime
from sqlalchemy import func

from model import User, Rating, Job, connect_to_db, db
from server import app

from API import get_api_data

# As a start, I'll have a list of users already defined in a text file
# Later, I want to implement a register option for adding new users 
def load_users():
    """Load users from u.user file into database."""

    print("Users")

    # Delete all rows in table, so if we need to run this a second time,
    # we won't be trying to add duplicate users
    User.query.delete()

    # Read u.user file and insert data
    for row in open("seed_data/u.user"):
        row = row.rstrip()
        user_id, fname, lname, email, password = row.split("|")

        user = User(user_id=user_id,
                    fname=fname,
                    lname=lname,
                    email=email,
                    password=password)


        # We need to add to the session or it won't ever be stored
        db.session.add(user)

    # Once we're done, we should commit our work
    db.session.commit()

def load_jobs():
    """Load jobs into database."""


    print("Jobs")
    # Delete all rows in table, so if we need to run this a second time,
    # we won't be trying to add duplicate users
    Job.query.delete()

    # Importing function that returns json of all CA job listings after API call 
    jobs_json = get_api_data()

    # Parse through API response and assign data to appropriate columns in job table 
    job_id = 1 # set first job_id to 1 and increment additional listings as +1 the current job_id
    for listing in jobs_json:
        
        job = Job(job_id = job_id,
                  title = listing['title'],
                  company = listing['company'],
                  location = listing['location'],
                  released_at = listing['created_at'],
                  github_job_uid = listing['id'])
    
        db.session.add(job)
        job_id += 1

    # Once we're done, we should commit our work
    db.session.commit()
    

#call api function to load data 

def load_ratings():
    """Load ratings into database."""







# def create_test_user() # put sample code of test users here -- how it backups ('test' as username for login)

if __name__ == "__main__":
    connect_to_db(app)

    # In case tables haven't been created, create them
    db.create_all()

    # Import different types of data
    load_users()
    load_jobs()
    load_ratings()

