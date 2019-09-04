
import requests
import json



EVENTBRITE_URL = "'https://www.eventbriteapi.com/v3/categories?token=W5TEINASBAG56UPMVLKI'"




# edit so that function only calls API for certain job instead of calling the API
# and then parsing through it. 

def get_api_data():
    """Calls API, returns a string object of job listings in CA. Parsing through list to populate columns """

    # searching for jobs in California only to populate jobs table in database
    url = 'https://jobs.github.com/positions.json?location=California'

    response = requests.get(url)
    data = response.json()
    

    return data # this returned a list of job listing objects 


################################################################################
################################################################################
def get_events_api():
    """Calls Eventbrite API and returns a list of events catered to User's progress"""


    #this is for tech networking events only  
    payload = {'token' : 'W5TEINASBAG56UPMVLKI'}
    url = "https://www.eventbriteapi.com/v3/events/search/?q=tech+networking&sort_by=date&location.address=California"

    response = requests.get(url, params=payload)

    data = response.json()

    return data
    




get_events_api()

