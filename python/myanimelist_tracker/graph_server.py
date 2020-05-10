import os
import time
import threading
import myanimelist_tracker
from flask import Flask, request

# For storing the data recorded by the tracker in memory
data = []


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
        # header = open('templates/header.html').read()
        # footer = open('templates/footer.html').read()
        # header = header.replace('$CSS_PATH', path_to_css)

        return str(data)

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
