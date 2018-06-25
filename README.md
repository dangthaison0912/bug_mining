This is the summary of the project architecture.

Requirement:
python3
BeautifulSoup





Path to source code: virtualenvfolder/bugmining/mining_main

BACKEND

bug_id_scraping.py:
Mine the bug information in Chromium Bug Blog in the research stage
Not currently in used for the project

js_scraping.py:
Scrape information in Javascript forms in the research stage
Not currently in used for the project

classifier.py:
The main logic of the Naive Bayes Classifier

code_metrics_scraping.py:
Scrape the file information from the Gerrit (Google git)


WEB APPLICATION

views.py:
Connect the BACKEND to the FRONTEND, control the flow of the data

models.py:
Objects information and how they are stored in the database


HOW TO RUN:
1.Activate virtual environment in virtualenvfolder/bin: source activate
2.Run web application in virtualenvfolder/bugmining/manage.py: python3 manage.py runserver
3.Open browser and go to http://127.0.0.1:8000/mining_main/
4.Follow instruction on the front page
