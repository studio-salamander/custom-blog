# custom-blog
Example of web application (custom blog), created by using Python 3.6 + Flask microframework + sqlite
# Installation
Install the requirements package:

pip install -r requirements.txt

The sqlite database must be created before the application can run, and the db_create.py script takes care of that.

python db_create.py

# Running
To run the application in the development web server just execute run.py (debug=True) or runp.py (debug=False) with the Python interpreter from the flask virtual environment.

python run.py
