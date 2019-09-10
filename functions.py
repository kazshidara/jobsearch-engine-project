
from model import connect_to_db, db, User, Job, Rating

from datetime import datetime, date


def days_from_date(job_date):
    """Returns the time in days between today's date and the date of the job posting"""

    current_date = datetime.today()
    time_difference = current_date - job_date
    number_of_days = time_difference.days

    return number_of_days



