"""Models and database functions for Job Search project."""

from flask_sqlalchemy import SQLAlchemy

# This is the connection to the PostgreSQL database; we're getting
# this through the Flask-SQLAlchemy helper library. On this, we can
# find the `session` object, where we do most of our interactions
# (like committing, etc.)

db = SQLAlchemy()


#####################################################################
# Model definitions

class User(db.Model):
    """User of jobs website."""

    __tablename__ = "users_table"

    user_id = db.Column(db.Integer,
                        autoincrement=True,
                        primary_key=True)
    fname = db.Column(db.String(50), nullable=False)
    lname = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(20), nullable=False)
    #columns to see if user has had past experience applying to a company (2)

    
    # can do user.saved to get all jobs that user saved
    saved_jobs = db.relationship("Job",
                                 secondary="saved_table",
                                 backref=db.backref("users_saved"))
    
    def __repr__(self):
        """Provide helpful representation when printed."""

        return f"<User user_id={self.user_id} email={self.email}>"


class Job(db.Model):
    """Job on jobs website."""

    __tablename__ = "jobs_table"

    job_id = db.Column(db.Integer,
                         autoincrement=True,
                         primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    company = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    released_at = db.Column(db.DateTime, nullable=True)
    # job_url = db.Column(db.String, nullable=False, )
    github_job_uid = db.Column(db.String, nullable=False, index=True, unique=True)
    #able to index into this column for each job listing if user wants more info about a particular job

    def __repr__(self):
        """Provide helpful representation when printed."""

        return f"<Job company={self.company} title={self.title}>"


    #CREATE METHODS that take a job instance and calculates the average rating 


class Rating(db.Model):
    """Rating of a job (posting) by a user."""

    __tablename__ = "ratings_table"
    __table_args__ = (db.UniqueConstraint('job_id', 'user_id'),)

    rating_id = db.Column(db.Integer,
                          autoincrement=True,
                          primary_key=True)
    job_id = db.Column(db.Integer, db.ForeignKey('jobs_table.job_id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users_table.user_id'), nullable=False)
    rating = db.Column(db.Integer, nullable=True)


   
    
    
    # Define relationship to user
    user = db.relationship("User",
                           backref=db.backref("ratings",
                                              order_by=rating_id))     

   

    # Define relationship to job
    job = db.relationship("Job",
                            backref=db.backref("ratings",
                                               order_by=rating_id))

    def __repr__(self):
        """Provide helpful representation when printed."""

        return f"""<Rating rating_id={self.rating_id}
                   job_id={self.job_id}
                   user_id={self.user_id}
                   rating={self.rating}>"""


class Savings(db.Model):
    """All the jobs that were saved by a user."""

    __tablename__ = "saved_table"
    __table_args__ = (db.UniqueConstraint('job_id', 'user_id'),)

    saved_id = db.Column(db.Integer,
                          autoincrement=True,
                          primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users_table.user_id'), nullable=False)
    job_id = db.Column(db.Integer, db.ForeignKey('jobs_table.job_id'), nullable=False)
    
    def __repr__(self):
        """Provide helpful representation when printed."""

        return f"""<job_id={self.job_id}
                   user_id={self.user_id}>"""

 



   
 


#####################################################################
# Helper functions

def connect_to_db(app):
    """Connect the database to our Flask app."""

    # Configure to use our PostgreSQL database
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///mydatabase'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.app = app
    db.init_app(app)


if __name__ == "__main__":
    # As a convenience, if we run this module interactively, it will
    # leave you in a state of being able to work with the database
    # directly.

    from server import app
    connect_to_db(app)
    print("Connected to DB.")
