
"""
Scraper for POLYHAVEN
You need BeautifulSoup
run this command in cmd "pip install bs4"
"""


import urllib.request
from bs4 import BeautifulSoup

import os
import json


agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) ' \
        'Chrome/35.0.1916.47 Safari/537.36'


def retry_on_failure(default_value='', attempts=5):

    """
    This will allow us to retry without crashing the entire program.

    """

    def decorator(func):

        def new_func(*args, **kwargs):

            for _ in range(attempts):
                try:
                    return func(*args, **kwargs)

                except Exception as e:

                    print('error: %s' % e)
                    continue

        return new_func

    return decorator


@retry_on_failure()
def soup_it(url):

    """
    Creates a fake browser agent, soups the contents

    """

    req = urllib.request.Request(
        url,
        data=None,
        headers={
            'User-Agent': agent
        }
    )

    return BeautifulSoup(urllib.request.urlopen(req).read().decode('utf-8'), 'html.parser')


@retry_on_failure()
def download_it(res, url, download_dir, thumbnail_url, info, checker=None):

    file_name = url.split('/')[-1]
    base_name = file_name.split('_%s.' % res)[0]
    base_path = os.path.join(download_dir, base_name)

    if os.path.exists(base_path) is False:
        os.mkdir(base_path)

    file_path = os.path.join(base_path, file_name)
    thumb_path = os.path.join(base_path, 'thumbnail.jpg')
    checker_path = os.path.join(base_path, 'checker.zip')

    if os.path.exists(file_path) is False:
        print('downloading: %s to %s' % (url, file_path))

        # Set urllib parameters
        opener = urllib.request.build_opener()
        opener.addheaders = [('User-Agent', agent)]
        urllib.request.install_opener(opener)

        # Write Thumb
        urllib.request.urlretrieve(thumbnail_url, thumb_path)

        # Write EXR
        urllib.request.urlretrieve(url, file_path)

        # Write Checker
        if checker:
            urllib.request.urlretrieve(checker, checker_path)

        # Write Metadata
        if info:

            metadata_path = os.path.join(base_path, 'info.json')
            with open(metadata_path, 'w') as f:
                data = json.dumps(info)
                f.write(data)
    else:
        print('skipping: %s' % file_path)


def main(download_dir, res='4k'):

    base_url = "https://polyhaven.com"
    url = base_url + '/textures'

    contents = soup_it(url)

    # contents = soup_it(link)
    item_grid = contents.find('div', attrs={'class': 'Page_pageContent__3M2vs'})
    item_links = []

    for item in item_grid:

        print(item)

        """
        thumbnail_url = '%s%s' % (base_url, item.find('img', attrs={'class': 'thumbnail'}).attrs['data-src'])
        href = item.attrs['href']
        item_url = '%s%s' % (base_url, href)
        item_links.append(item_url)

        contents = soup_it(item_url)
        download_buttons = contents.find_all('div', attrs={'class': 'download-buttons'})
        info_contents = contents.find('ul', attrs={'class': 'item-info-list'})
        b_elements = info_contents.find_all('b')
        info = {}

        # Try and get info
        for b in b_elements:
            text = b.text

            if text == "Whitebalance:":
                white_bal = b.next_sibling
                info['white_bal'] = int(white_bal)

            if text == "Categories:":
                categories = []
                categories_group = [x for x in list(b.next_siblings) if x and ', ' not in x]
                for c in categories_group:
                    try:
                        categories.append(c.contents[0])
                    except AttributeError:
                        pass
                info['keywords'] = categories

        full_href = None
        checker = None

        for button_container in download_buttons:

            for button in button_container.children:

                try:
                    href = button.attrs['href']
                    # Prevent things like 24k. lol
                    if '_%s' % res in href:
                        full_href = href

                    # Check for macbeth link
                    if 'Color Charts' in href:
                        checker = href.replace(' ', '%20')

                except KeyError:
                    pass

        # DO DOWNLOAD HERE
        download_it(res, full_href, download_dir, thumbnail_url, info, checker)
        """

    print('---------------------------')


if __name__ == "__main__":

    # Location of output
    main('Z:\\share\\hdrihaven')
