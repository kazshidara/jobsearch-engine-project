# metaSearch

A personalized and interactive job search engine that displays active job postings and keeps track of your progress.  

## Tech Stack

Frontend: Javascript (AJAX),jQuery, HTML5/CSS, Bootstrap

Backend: Python, Flask, PostgreSQL, SQLAlchemy, SQL, Chart.js

APIs: Github Jobs, Eventbrite


## Features

1. Create an account or Login 

![alttext](https://raw.githubusercontent.com/kazshidara/jobsearch-engine-project/master/static/images/registration.png)


2. Search for active job posting via job titles or preferred location

![alttext](https://raw.githubusercontent.com/kazshidara/jobsearch-engine-project/master/static/images/search.png)


3. Save jobs in personal profile for later reference

![alttext](https://raw.githubusercontent.com/kazshidara/jobsearch-engine-project/master/static/images/save.png)


4. Registered and Logged in users can track their current job search progress 

![alttext](https://raw.githubusercontent.com/kazshidara/jobsearch-engine-project/master/static/images/progress.png)


5. Aggregates feedback/responses from all users of the app to display what application process is like for each hiring company

![alttext](https://raw.githubusercontent.com/kazshidara/jobsearch-engine-project/master/static/images/rating.png)

![alttext](https://raw.githubusercontent.com/kazshidara/jobsearch-engine-project/master/static/images/job.png)


6. Based on individual user’s progress, metaSearch recommends tech/engineering events that are catered to each person’s needs

![alttext](https://raw.githubusercontent.com/kazshidara/jobsearch-engine-project/master/static/images/recEvents.png)




## Setup/Installation 

### Requirements:

PostgreSQL

Python3

Eventbrite API keys

### How to successfully launch the app has been outlined below:

Clone repository:
```
$ https://github.com/kazshidara/jobsearch-engine-project.git
```
 
Create a virtual environment:
```
$ virtualenv env
```
 
Activate the virtual environment and run file with secret keys :
```
$ source env/bin/activate
$ source secrets.sh
```

Install dependencies:
```
$ pip3 install -r requirements.txt
```
 
Make an account and retrieve your secret keys for Eventbrite. Save them to a file secrets.py which should look something like this:
```
export EVENTBRITE_KEY="M2MGJWKDK2442S"
export SECRET_KEY="mysecretkey"
```

Create database ‘jobs’:
```
$ createdb jobs
```
 
Create your database tables and seed example data, if you have any.
```
$ python3 model.py
$ python3 seed.py
```
 
Run the app from the command line.
```
$ python3 server.py
```


## License
This project is licensed under the MIT License - see the LICENSE.md file for details

## Acknowledgments

My fellow Hackbright cohort who inspired me to build this app, may we all find jobs in the coming weeks and continue to build 
