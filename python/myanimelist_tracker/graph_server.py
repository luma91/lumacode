import os
import time
import threading
import myanimelist_tracker
from flask import Flask, request, url_for

# For storing the data recorded by the tracker in memory
data = []

# Make sure working directory is the same as the script directory.
abspath = os.path.dirname(os.path.abspath(__file__))
os.chdir(abspath)


def web_server():

    """
    This is the flask server app.
    This will display the contents of the data for the rating tracker.

    """

    global data
    app = Flask(__name__)

    @app.route("/", methods=['GET'])
    def home():

        current_time = str(int(time.time()))
        path_to_css = 'static/css/stylesheet.css?' + current_time
        page_template = open('static/templates/index.html').read()
        page = page_template

        # Define Content Here
        page_title = 'Myanimelist Tracker'
        content = 'test content'

        # Compile the page
        page = page.replace('${STYLESHEET_PATH}', path_to_css)
        page = page.replace('${PAGE_CONTENT}', content)
        page = page.replace('${PAGE_TITLE}', page_title)
        return page

    # Run App
    app.run(host='0.0.0.0', port=8080)


def tracker_thread():

    """
    A simple loop for reading the data off disk and storing into a global var "data".
    This will run on an interval and refresh every 240 seconds.

    """

    global data

    while True:
        data = myanimelist_tracker.read_data()
        time.sleep(240)


if __name__ == "__main__":

    t = threading.Thread(target=tracker_thread)
    t.start()
    web_server()
