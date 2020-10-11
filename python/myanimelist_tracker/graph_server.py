import os
import time
import random
import myanimelist_tracker
from collections import OrderedDict
from datetime import datetime, timedelta
from flask import request, Blueprint

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


anime_tracker = Blueprint('anime-tracker', __name__)


@anime_tracker.route('/anime-tracker', methods=['GET'])
def webpage():

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
    filter_broadcast = request.args.get('broadcast')
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

    if filter_broadcast is None:
        filter_broadcast = 'both'

    show_data = []
    num = 1

    if data:

        # Sort by Ranking (Of last entry)
        sorted_data = OrderedDict(
            sorted(data.items(), key=lambda y: y[1]['datapoints'][-1][0]['rank'], reverse=True)
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

            # Filter Broadcast Type
            if filter_broadcast:
                if str(filter_broadcast) == 'new':
                    if data[show]['continuing'] is True:
                        continue

                elif str(filter_broadcast) == 'continuing':
                    if data[show]['continuing'] is False:
                        continue

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

        if filter_broadcast:
            url += '&broadcast=%s' % filter_broadcast

        header += '<a href="%s" class="%s">%s</a>' % (url, link_class, season[0])

    header += '</div>'

    top_limits = [5, 10, 15, 20, 50, 100]
    header += '<div class="limit_display">Top: '

    for limit in top_limits:

        url = '?limit=' + str(limit)
        if filter_season:
            url += '&season=' + filter_season

        if filter_category:
            url += '&category=%s' % filter_category

        if filter_broadcast:
            url += '&broadcast=%s' % filter_broadcast

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

        if filter_broadcast:
            url += '&broadcast=%s' % filter_broadcast

        link_class = 'menu-item'
        if filter_category:
            if category.lower() == filter_category.lower():
                link_class += ' menu-active'
        header += '<a href="%s" class="%s">%s</a>' % (url, link_class, category)

    header += '</div>'

    broadcast_types = ['new', 'continuing', 'both']
    header += '<div class="category">Broadcast Type: '

    for x in broadcast_types:
        url = '?broadcast=' + x

        if result_limit and result_limit != default_limit:
            url += '&limit=%s' % str(result_limit)

        if filter_season:
            url += '&season=' + filter_season

        if filter_category:
            url += '&category=%s' % filter_category

        if filter_broadcast:
            url += '&broadcast=%s' % filter_broadcast

        link_class = 'menu-item'
        if filter_broadcast:
            if x.lower() == filter_broadcast.lower():
                link_class += ' menu-active'

        header += '<a href="%s" class="%s">%s</a>' % (url, link_class, x.title())

    header += '</div>'

    header += '<div class="search_field">'
    header += '<form id="search_form" method="GET">'
    header += '<input type="text" id="title" placeholder="Type Show Name"  name="title"></input>'
    header += '<input type="submit"></input>'
    header += '</form>'
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
