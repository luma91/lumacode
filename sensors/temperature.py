# https://www.crummy.com/software/BeautifulSoup/bs4/doc/

import urllib.request
from bs4 import BeautifulSoup

url = "https://weather.com/weather/today/l/-37.81,144.96?unit=m"
agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) ' \
        'Chrome/35.0.1916.47 Safari/537.36'

req = urllib.request.Request(
    url,
    data=None,
    headers={
        'User-Agent': agent
    }
)


def get_temp():

    soup = BeautifulSoup(urllib.request.urlopen(req).read().decode('utf-8'), 'html.parser')
    element = soup.find('span', attrs={'data-testid': 'TemperatureValue'})
    temp = element.contents[0]

    temp_formatted = []
    for x in temp:
        if x.isnumeric() or '.' in x:
            temp_formatted.append(x)

    temp_formatted = float(''.join(temp_formatted))

    print('Current Temp: %sC' % temp_formatted)
    return temp_formatted


if __name__ == "__main__":
    get_temp()
