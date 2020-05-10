import os
import time
import threading
import json
import myanimelist_tracker
from flask import Flask, request

# For storing the data recorded by the tracker in memory
data = []

# Make sure working directory is the same as the script directory.
abspath = os.path.dirname(os.path.abspath(__file__))
os.chdir(abspath)


def web_server():

    """
    This is the flask server app.
    This will display the contents of the data for the rating tracker.

    Chart.js examples:
    https://www.chartjs.org/samples/latest/
    https://www.chartjs.org/docs/latest/charts/line.html
    https://tobiasahlin.com/blog/chartjs-charts-to-get-you-started

    """

    global data
    app = Flask(__name__)

    @app.route("/", methods=['GET'])
    def home():

        current_time = str(int(time.time()))
        path_to_css = 'static/css/stylesheet.css?' + current_time
        page_template = open('static/templates/index.html').read()
        line_graph_template = open('static/templates/charts/line_graph.html').read()
        page = page_template

        # Define Graph Contents Here
        graph_labels = ['test']
        graph_data = {
            'data': [86, 114, 106, 106, 107, 111, 133, 221, 783, 2478],
            'label': "Africa",
            'borderColor': "#3e95cd",
            'fill': False
        }

        line_graph = line_graph_template.replace('${GRAPH_DATA}', json.dumps(graph_data))
        line_graph = line_graph.replace('${GRAPH_LABELS}', json.dumps(graph_labels))
        line_graph = line_graph.replace('${GRAPH_TITLE}', 'Ranking')

        # Define Content Here
        page_title = 'MyAnimeList.net - Ranking Tracker'
        content = line_graph

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
