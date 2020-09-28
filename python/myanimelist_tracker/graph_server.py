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


def make_color():
    color_value = random.randint(25, 215)
    return color_value


def convert_timestamp(timestamp):

    """
    Converts a Timestamp into a readable Date.

    """

    dt_object = datetime.fromtimestamp(timestamp)
    formatted_output = datetime.strftime(dt_object, '%d/%m/%y %H:%M:%S')
    return dt_object, formatted_output


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

        season_data = myanimelist_tracker.read_season_data()
        current_season = season_data['current_season']
        data = myanimelist_tracker.read_data()
        current_time = str(int(time.time()))
        path_to_css = 'static/css/stylesheet.css?' + current_time
        page_template = open('static/templates/index.html').read()
        line_graph_template = open('static/templates/charts/line_graph.html').read()
        page = page_template

        # Define and Set Result Limit
        result_limit = request.args.get('limit')
        weeks_back = request.args.get('weeks_back')
        filter_season = request.args.get('season')
        filter_title = request.args.get('title')
        filter_category = request.args.get('category')
        default_limit = 15
        default_category = 'TV'

        if result_limit:
            result_limit = int(result_limit)

        else:
            result_limit = default_limit

        if filter_season is None:
            filter_season = current_season

        if filter_category is None:
            filter_category = default_category

        show_data = []
        num = 1

        if data:

            # Sort by Ranking (Of last entry)
            sorted_data = OrderedDict(
                sorted(data.items(), key=lambda x: x[1]['datapoints'][-1][0]['rank'], reverse=True)
            )

            for show in sorted_data:

                # Season Filter
                if filter_season:
                    if str(filter_season.replace('_', ' ')).lower() not in data[show]['season'].lower():
                        continue

                # Filter Name
                if filter_title:
                    if str(filter_title).lower() not in data[show]['title'].lower():
                        continue

                # Filter Category (tv, movie, ova, etc..)
                try:
                    if filter_category:
                        if filter_category.lower() not in data[show]['category'].lower():
                            continue
                except KeyError:
                    print('WARNING: cannot_get_category: %s' % show)

                # Result Limit (This has to be last!)
                if num <= result_limit:

                    color = '%02X%02X%02X' % (make_color(), make_color(), make_color())
                    title = data[show]['title']
                    datapoints = data[show]['datapoints']
                    rank_samples = []
                    rank_samples_formatted = ''

                    for sample in datapoints:
                        sample_time = convert_timestamp(sample[1])

                        # If weeks defined, skip samples before this time.
                        if weeks_back:
                            now = datetime.now()
                            td = timedelta(weeks=int(weeks_back))
                            if now - td > sample_time[0]:
                                continue

                        sample_data = sample[0]['rank']
                        rank_samples.append('{x: "' + sample_time[1] + '", y: ' + str(sample_data) + '}')
                        rank_samples_formatted = ', '.join(rank_samples)

                    show_data.append('{ label: "' + title + '", data: [' + rank_samples_formatted + '], borderColor: "#' + color + '", fill: false }')
                    num += 1

        graph_data = ', '.join(show_data)
        line_graph = line_graph_template.replace('${GRAPH_DATA}', graph_data)

        # Define Content Here
        page_title = 'Anime Ranking Tracker'
        content = line_graph

        header = '<div class="menu">'

        header += '<div class="seasons">Season: '
        for season in season_data['seasons']:
            link_class = 'menu-item'

            if filter_season:
                if season[0] in filter_season.replace('_', ' '):
                    link_class += ' menu-active'

            url = '?season=%s' % season[0].replace(' ', '_')

            if result_limit and result_limit != default_limit:
                url += '&limit=%s' % str(result_limit)

            if filter_category:
                url += '&category=%s' % filter_category

            header += '<a href="%s" class="%s">%s</a>' % (url, link_class, season[0])

        header += '</div>'

        top_limits = [10, 15, 20, 50, 100]
        header += '<div class="limit_display">Top: '

        for limit in top_limits:

            url = '?limit=' + str(limit)
            if filter_season:
                url += '&season=' + filter_season

            if filter_category:
                url += '&category=%s' % filter_category

            link_class = 'menu-item'
            if result_limit:
                if str(limit) == str(result_limit):
                    link_class += ' menu-active'

            header += '<a href="%s" class="%s">%s</a>' % (url, link_class, limit)

        header += '</div>'

        category_limits = ['TV', 'ONA', 'OVA', 'Movie', 'Special']
        header += '<div class="category">Category: '

        for category in category_limits:
            url = '?category=' + category

            if result_limit and result_limit != default_limit:
                url += '&limit=%s' % str(result_limit)

            if filter_season:
                url += '&season=' + filter_season

            link_class = 'menu-item'
            if filter_category:
                if category.lower() == filter_category.lower():
                    link_class += ' menu-active'
            header += '<a href="%s" class="%s">%s</a>' % (url, link_class, category)

        header += '</div>'
        header += '</div>'

        if filter_title:
            header += '<div class="filter_title">Filtering results by: <b>%s</b></div>' % filter_title.title()

        # Compile the page
        page = page.replace('${STYLESHEET_PATH}', path_to_css)
        page = page.replace('${HEADER}', header)
        page = page.replace('${PAGE_CONTENT}', content)
        page = page.replace('${PAGE_TITLE}', page_title)

        return page

    # Run App
    app.run(host='0.0.0.0', port=8080)


if __name__ == "__main__":
    web_server()
