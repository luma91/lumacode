# https://realpython.com/beautiful-soup-web-scraper-python/
# https://www.geeksforgeeks.org/implementing-web-scraping-python-beautiful-soup/

import urllib.request
from bs4 import BeautifulSoup

# Base URL
url = 'http://myanimelist.net/anime/season'


def gather_ratings():

    output = []

    request = urllib.request.Request(url)
    response = urllib.request.urlopen(request)
    soup = BeautifulSoup(response, 'html.parser')
    elements = soup.find_all('div', attrs={'class': 'seasonal-anime js-seasonal-anime'})

    for item in elements:
        show_data = {'title': item.find('a', attrs={'class': 'link-title'}).text.strip(),
                     'rating': item.find('span', attrs={'title': 'Score'}).text.strip(),
                     'popularity': item.find('span', attrs={'title': 'Members'}).text.strip(),
                     'url': item.find('a', attrs={'class': 'link-title'})['href']}

        # Filter results with no applicable rating.
        if 'N/A' not in show_data['rating']:
            output.append(show_data)

    return output


# Example on gathering data
if __name__ == "__main__":

    data = gather_ratings()
    for show in data:
        print(show)
