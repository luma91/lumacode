# https://www.crummy.com/software/BeautifulSoup/bs4/doc/

import urllib.request
from bs4 import BeautifulSoup

url = "https://www.weatherzone.com.au/vic/melbourne/camberwell"


def get_temp():
    html_doc = urllib.request.urlopen(url).read()
    soup = BeautifulSoup(html_doc, 'html.parser')
    element = soup.find('span', attrs={'class': 'tempnow'})
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
