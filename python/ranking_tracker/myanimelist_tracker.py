# https://realpython.com/beautiful-soup-web-scraper-python/
# https://www.geeksforgeeks.org/implementing-web-scraping-python-beautiful-soup/

import urllib.request
import json
import os
import time
import threading
from datetime import datetime
from bs4 import BeautifulSoup

# Base URL
url = 'http://myanimelist.net/anime/season'
database = '/mnt/Dropbox/ranking_tracker.json'


def gather_ratings():

    """
    This is the main part that will go to the URL defined above and scrape the page for info.
    Returns a list of dictionaries, each contains data for a show, rating, popularity and URL.

    """

    print('gathering data from web.')

    output = []
    request = urllib.request.Request(url)
    response = urllib.request.urlopen(request)
    soup = BeautifulSoup(response, 'html.parser')
    elements = soup.find_all('div', attrs={'class': 'seasonal-anime js-seasonal-anime'})

    for item in elements:
        rating = item.find('span', attrs={'title': 'Score'}).text.strip()
        popularity = item.find('span', attrs={'title': 'Members'}).text.strip().replace(',', '')

        if 'N/A' not in rating:
            show_data = {'title': item.find('a', attrs={'class': 'link-title'}).text.strip(),
                         'rating': float(rating),
                         'popularity': int(popularity),
                         'url': item.find('a', attrs={'class': 'link-title'})['href']}

            output.append(show_data)

    return output


def make_timestamp():

    """
    Make a timestamp for logging to the JSON file
    Strips the decimal places, returns an integer.

    """

    now = datetime.now()
    return int(now.timestamp())


def read_data():

    """
    Read the data from disk.
    Returns a list.

    """

    if os.path.exists(database):

        print('reading from disk.')
        with open(database, 'r') as json_file:
            data = json.load(json_file)

        return data


def write_data(input_data):

    # Will append a timestamp to the input_data

    # Will attempt to collect old data
    result_data = input_data

    # If there is data already on disk, we will append the new results with a timestamp as a sample.
    print('writing to disk.')
    with open(database, 'w+') as json_file:
        json.dump(result_data, json_file, indent=1)


def convert_to_samples(input_data):

    """
    This will convert each entry in the database into a set of samples, or append the current sample to the list
    for each entry (If already processed).

    """

    timestamp = make_timestamp()
    data_from_disk = read_data()
    output_data = []

    # File not on disk, will not append.

    for show in input_data:

        rating = show['r']
        popularity = show['p']

        # Create a sample
        sample_data = [{'r': rating, 'p': popularity}, timestamp]
        new_data = {
            'title': show['title'],
            'url': show['url'],
            'datapoints': sample_data
        }

        if data_from_disk:
            for x in data_from_disk:
                if x['title'] == show['title']:
                    datapoints = x['datapoints']
                    datapoints.append(sample_data)

                    new_data = {
                        'title': show['title'],
                        'url': show['url'],
                        'datapoints': datapoints
                    }

        output_data.append(new_data)

    return output_data


def process_data():

    """
    The main loop which will run on an interval and trigger the gather_ratings() function.
    Does not return anything.

    """

    while True:
        data = gather_ratings()
        new_data = convert_to_samples(data)
        write_data(new_data)

        # Standard Wait Period before collecting new results.
        # 1 Day
        time.sleep(86400)


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
