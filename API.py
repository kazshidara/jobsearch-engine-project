
import requests
import json
from sys import argv
from pprint import pformat


def get_api_data():
    """Calls API, returns a string object of job listings in CA. Parsing through list to populate columns """

    # searching for jobs in California only to populate jobs table in database
    url = 'https://jobs.github.com/positions.json?location=California'

    response = requests.get(url)
    data = response.json()
    return data # this returned a list of job listing objects 
    


get_api_data()

# this returns string representation of all the job listings in California
# as a list of ditionaries for each job listing 


#once you set up model.py and connect Flask to SQLAlchemy, 
# create seed.py that loads this function into database 


