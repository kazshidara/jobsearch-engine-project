
import requests
import json
from sys import argv
from pprint import pformat


# edit so that function only calls API for certain job instead of calling the API
# and then parsing through it. 

def get_api_data():
    """Calls API, returns a string object of job listings in CA. Parsing through list to populate columns """

    # searching for jobs in California only to populate jobs table in database
    url = 'https://jobs.github.com/positions.json?location=California'

    response = requests.get(url)
    data = response.json()
    
    



    return data # this returned a list of job listing objects 
    


get_api_data()






