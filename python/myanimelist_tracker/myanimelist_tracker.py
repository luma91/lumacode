# https://realpython.com/beautiful-soup-web-scraper-python/
# https://www.geeksforgeeks.org/implementing-web-scraping-python-beautiful-soup/

import urllib.request
import json
import os
import time
import threading
import config
from uuid import uuid4
from datetime import datetime, timedelta
from bs4 import BeautifulSoup


def gather_ratings():

    """
    This is the main part that will go to the URL defined above and scrape the page for info.
    Returns a list of dictionaries, each contains data for a show, rating, popularity and URL.

    """

    print('gathering data from web.')

    output = []
    request = urllib.request.Request(config.myanimelist_url)
    response = urllib.request.urlopen(request)
    soup = BeautifulSoup(response, 'html.parser')
    elements = soup.find_all('div', attrs={'class': 'seasonal-anime js-seasonal-anime'})

    for item in elements:
        title = item.find('a', attrs={'class': 'link-title'}).text.strip()
        url = item.find('a', attrs={'class': 'link-title'})['href']
        rating = item.find('span', attrs={'title': 'Score'}).text.strip()
        popularity = item.find('span', attrs={'title': 'Members'}).text.strip().replace(',', '')

        # Ignore shows with a non applicable rating.
        if 'N/A' not in rating:
            show_data = {'title': title,
                         'url': url,
                         'rank': float(rating),
                         'popularity': int(popularity)}

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

    if os.path.exists(config.data_directory):

        print('reading from disk.')

        data = {}
        files = os.listdir(config.data_directory)

        for f in files:
            show_path = os.path.join(config.data_directory, f)
            with open(show_path, 'r') as json_file:
                data.update({f: json.load(json_file)})

        if data:
            return data


def write_data(input_data):

    # If there is data already on disk, we will append the new results with a timestamp as a sample.
    print('writing to disk.')

    for show in input_data:

        file_name = show['file_name']
        data = show['data']
        show_path = os.path.join(config.data_directory, file_name)

        with open(show_path, 'w+') as json_file:
            json.dump(data, json_file, indent=1)

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
            'datapoints': sample_data
        }}

        if data_from_disk:

            for x in data_from_disk:

                file_name = x
                file_data = data_from_disk[x]

                # If show exists
                if file_data['title'] == show['title']:
                    datapoints = file_data['datapoints']
                    datapoints.append(sample_data)

                    new_data = {'file_name': file_name, 'data': {
                        'title': show['title'],
                        'url': show['url'],
                        'datapoints': datapoints
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

        # Process the data and append to old data
        new_data = convert_to_samples(data)

        # Write the new data to disk
        write_data(new_data)

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
