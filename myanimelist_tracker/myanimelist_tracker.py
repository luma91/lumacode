# https://realpython.com/beautiful-soup-web-scraper-python/
# https://www.geeksforgeeks.org/implementing-web-scraping-python-beautiful-soup/

import json
import os
import threading
import time
import urllib.request
from datetime import datetime, timedelta
from uuid import uuid4

import config
from bs4 import BeautifulSoup

# Full Path
full_path = os.path.join(config.base_path, config.data_directory)


def month_to_season(start_date):

    """
    Get season from month

    """

    seasons = {
        'spring': ['mar', 'apr', 'may'],
        'summer': ['jun', 'jul', 'aug'],
        'fall': ['sep', 'oct', 'nov'],
        'winter': ['dec', 'jan', 'feb']
    }

    for season in seasons:

        # Return the season
        season_months = seasons[season]

        for month in season_months:
            if month in start_date.lower():
                return season


def gather_ratings():

    """
    This is the main part that will go to the URL defined above and scrape the page for info.
    Returns a list of dictionaries, each contains data for a show, rating, popularity and URL.

    """

    print('gathering data from web.')

    output = []
    seasons = get_season_data()['seasons']

    for season in seasons:

        print('processing: %s at url: %s' % (season[0], season[1]))

        request = urllib.request.Request(season[1])
        response = urllib.request.urlopen(request)
        soup = BeautifulSoup(response, 'html.parser')

        elements = soup.find_all('div', attrs={'class': 'seasonal-anime js-seasonal-anime'})
        current_season = season[0]

        num_success = 0
        num_empty = 0
        for item in elements:
            title = item.find('a', attrs={'class': 'link-title'}).text.strip()
            url = item.find('a', attrs={'class': 'link-title'})['href']
            rating = item.find('span', attrs={'title': 'Score'}).text.strip()
            popularity = item.find('span', attrs={'title': 'Members'}).text.strip().replace(',', '')
            info = item.find('div', attrs={'class': 'info'}).text
            category = ''.join(info.split()).split('-')[0]
            continuing = True

            start_date_string = info.split('-')[1].strip()
            start_date_split = start_date_string.split(', ')
            if len(start_date_split) > 1:
                start_date, start_year = start_date_split[0], start_date_split[1]

                # Replace ?? Entries with the 1st.
                start_date = start_date.replace('??', '1')
                start_season = month_to_season(start_date)

                # Check if show is continuing.
                if start_season and start_season.lower() in current_season.lower():

                    if start_year in current_season:
                        continuing = False

                        # print('%s is NEW. start_date: %s. start_season: %s. current_season: %s' %
                        # (title, start_date_string, start_season, current_season))

            else:
                print('ERROR! no date: %s' % title)

            # Ignore shows with a non applicable rating.
            if 'N/A' not in rating:
                show_data = {'title': title,
                             'url': url,
                             'season': current_season,
                             'rank': float(rating),
                             'popularity': int(popularity),
                             'category': category,
                             'continuing': continuing}

                output.append(show_data)
                num_success += 1

            else:
                num_empty += 1

        print('num_success: %s num_empty: %s' % (num_success, num_empty))

    return output


def make_timestamp():

    """
    Make a timestamp for logging to the JSON file
    Strips the decimal places, returns an integer.

    """

    now = datetime.now()
    return int(now.timestamp())


def get_season_data():

    request = urllib.request.Request('http://myanimelist.net/anime/season')
    response = urllib.request.urlopen(request)
    soup = BeautifulSoup(response, 'html.parser')
    current_season = soup.find('a', attrs={'class': 'on'}).text.strip()
    print('current_season: %s' % current_season)

    # Get Seasons
    seasons = []
    horiznav_nav = soup.find('div', attrs={'class': 'horiznav_nav'})
    elements = horiznav_nav.findChildren('a')
    blacklist = ['Archive', 'Schedule', 'Later', '...']
    for element in elements:
        season = element.text.strip(), element['href']

        if season[0] not in blacklist:
            seasons.append(season)

    season_data = {'current_season': current_season, 'seasons': seasons}

    return season_data


def read_season_data():

    season_file_path = os.path.join(config.base_path, 'season_data.json')
    if os.path.exists(season_file_path):
        with open(season_file_path, 'r') as season_file:
            season_data = json.load(season_file)

    return season_data


def read_data():

    """
    Read the data from disk.
    Returns a list.

    """
    if os.path.exists(full_path):

        print('reading from disk.')

        data = {}
        files = os.listdir(full_path)

        for f in files:

            if f.startswith('.') is False:
                show_path = os.path.join(full_path, f)
                with open(show_path, 'r') as json_file:
                    data.update({f: json.load(json_file)})

        if data:
            return data


def write_data(input_data, season_data):

    # If there is data already on disk, we will append the new results with a timestamp as a sample.
    print('writing to disk.')

    for show in input_data:

        file_name = show['file_name']
        file_name = file_name.replace('/', '_')
        data = show['data']
        show_path = os.path.join(full_path, file_name)

        print('updating %s' % show_path)

        with open(show_path, 'w+') as json_file:
            json.dump(data, json_file, indent=1)

    # Write current season
    with open(os.path.join(config.base_path, 'season_data.json'), 'w+') as season_file:
        json.dump(season_data, season_file, indent=1)

    print('done.')


def convert_to_samples(input_data):

    """
    This will convert each entry in the database into a set of samples, or append the current sample to the list
    for each entry (If already processed).

    """

    timestamp = make_timestamp()
    data_from_disk = read_data()
    output_data = []

    for show in input_data:

        # Make a simple unique name for each JSON file that will
        # be stored in the data directory.
        file_title = show['title'].split(' ')[0]
        uid = str(uuid4()).split('-')[0]
        file_name = file_title + '_' + uid + '.json'

        # Create a sample
        sample_data = [{'rank': show['rank'], 'popularity': show['popularity']}, timestamp]
        new_data = {'file_name': file_name, 'data': {
            'title': show['title'],
            'url': show['url'],
            'season': show['season'],
            'category': show['category'],
            'continuing': show['continuing'],
            'datapoints': [sample_data]
        }}

        if data_from_disk:

            for x in data_from_disk:

                file_name = x
                file_data = data_from_disk[x]

                # If show exists
                if file_data['title'] == show['title']:
                    datapoints = file_data['datapoints']
                    new_datapoints = []
                    time_samples = []

                    default_gap = timedelta(hours=6)

                    # Filter for issues
                    for sample in file_data['datapoints']:

                        sample_time = datetime.fromtimestamp(sample[1])
                        sample_okay = True
                        for y in time_samples:
                            if default_gap > (sample_time - datetime.fromtimestamp(y)):
                                sample_okay = False
                                print('WARNING: %s has two samples too close. %s and %s' % (file_data['title'], datetime.fromtimestamp(y), sample_time))

                        # Check for Duplicates
                        if sample[1] not in time_samples:
                            if sample_okay is True:
                                new_datapoints.append(sample)

                        else:
                            print('WARNING: duplicate time-sample %s exists on %s. Skipping.' % (sample[1], file_data['title']))

                        # Add sample to processed samples.
                        time_samples.append(sample[1])

                    # Append Latest Sample
                    new_datapoints.append(sample_data)

                    new_data = {'file_name': file_name, 'data': {
                        'title': show['title'],
                        'url': show['url'],
                        'season': show['season'],
                        'category': show['category'],
                        'continuing': show['continuing'],
                        'datapoints': new_datapoints
                    }}

        output_data.append(new_data)

    return output_data


def process_data():

    """
    The main loop which will run on an interval and trigger the gather_ratings() function.
    Does not return anything.

    """

    while True:

        # Collect the latest ratings
        data = gather_ratings()

        season_data = get_season_data()

        # Process the data and append to old data
        new_data = convert_to_samples(data)

        # Write the new data to disk
        write_data(new_data, season_data)

        # Timeout until next cycle
        sleep_duration = timedelta(hours=24).total_seconds()
        time.sleep(sleep_duration)


def main():

    """
    This is the function to run in order to run the program. It will initiate the process_data function
    as a new thread.

    """

    # Run Main Processing Thread
    t = threading.Thread(target=process_data)
    t.start()


# Run the program
if __name__ == "__main__":
    main()
