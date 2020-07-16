import os
import time
import random
import myanimelist_tracker
from collections import OrderedDict
from datetime import datetime, timedelta
from flask import Flask, request

# Make sure working directory is the same as the script directory.
abspath = os.path.dirname(os.path.abspath(__file__))
os.chdir(abspath)
print(abspath)


def make_color():
    color_value = random.randint(25, 200)
    return color_value


def convert_timestamp(timestamp):

    """
    Converts a Timestamp into a readable Date.

    """

    dt_object = datetime.fromtimestamp(timestamp)
    output = datetime.strftime(dt_object, '%d/%m/%y %H:%M:%S')
    return output


def web_server():

    """
    This is the flask server app.
    This will display the contents of the data for the rating tracker.

    Chart.js examples:
    https://www.chartjs.org/samples/latest/
    https://www.chartjs.org/docs/latest/charts/line.html
    https://tobiasahlin.com/blog/chartjs-charts-to-get-you-started
    https://stackoverflow.com/questions/46626871/chart-js-use-time-for-xaxes/46659594
    https://embed.plnkr.co/JOI1fpgWIS0lvTeLUxUp/

    """
    app = Flask(__name__)

    @app.route("/", methods=['GET'])
    def home():

        data = myanimelist_tracker.read_data()
        current_time = str(int(time.time()))
        path_to_css = 'static/css/stylesheet.css?' + current_time
        page_template = open('static/templates/index.html').read()
        line_graph_template = open('static/templates/charts/line_graph.html').read()
        page = page_template

        # Define and Set Result Limit
        result_limit = request.args.get('limit')

        if result_limit:

            result_limit = int(result_limit)

        else:
            result_limit = 10

        show_data = []
        num = 1

        if data:

            # Sort by Ranking (Of last entry)
            sorted_data = OrderedDict(
                sorted(data.items(), key=lambda x: x[1]['datapoints'][-1][0]['rank'], reverse=True)
            )

            for show in sorted_data:

                if num <= result_limit:

                    color = '%02X%02X%02X' % (make_color(), make_color(), make_color())
                    title = data[show]['title']
                    datapoints = data[show]['datapoints']
                    rank_samples = []
                    rank_samples_formatted = ''

                    for sample in datapoints:

                        sample_time = convert_timestamp(sample[1])
                        sample_data = sample[0]['rank']
                        rank_samples.append('{x: "' + sample_time + '", y: ' + str(sample_data) + '}')
                        rank_samples_formatted = ', '.join(rank_samples)

                    show_data.append('{ label: "' + title + '", data: [' + rank_samples_formatted + '], borderColor: "#' + color + '", fill: false }')
                    num += 1

        graph_data = ', '.join(show_data)

        line_graph = line_graph_template.replace('${GRAPH_DATA}', graph_data)
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


if __name__ == "__main__":
    web_server()
