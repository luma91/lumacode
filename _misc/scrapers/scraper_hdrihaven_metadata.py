
"""
Scraper for HDRIHAVEN
You need BeautifulSoup
run this command in cmd "pip install bs4"
"""


import urllib.request
import os
import json
from bs4 import BeautifulSoup
import bs4


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
def download_it(res, url, download_dir, info):

    file_name = url.split('/')[-1]
    base_name = file_name.split('_%s.' % res)[0]
    base_path = os.path.join(download_dir, base_name)

    # make dir
    os.mkdir(base_path)

    # Set urllib parameters
    opener = urllib.request.build_opener()
    opener.addheaders = [('User-Agent', agent)]
    urllib.request.install_opener(opener)

    # Write Metadata
    if info:

        print('writing metadata: to %s' % base_path)

        metadata_path = os.path.join(base_path, 'info.json')
        with open(metadata_path, 'w') as f:
            data = json.dumps(info)
            f.write(data)


def main(download_dir, res='4k'):

    base_url = "https://hdrihaven.com"
    url = base_url + '/hdris'

    contents = soup_it(url)

    # contents = soup_it(link)
    item_grid = contents.find('div', attrs={'id': 'item-grid'})

    item_links = []

    for item in item_grid:
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

            if text == "Author:":
                author = b.next_sibling.text
                info['author'] = author

            if text == "Dynamic Range:":

                # x for str(x).lstrip() if isinstance(bs4.NavigableString) else x.href
                dynamic_range = ' '.join([x.lstrip() if isinstance(x, bs4.NavigableString) else x.text for x in list(b.next_siblings)])
                info['dynamic_range'] = dynamic_range

            if text == "Whitebalance:":
                white_bal = b.next_sibling
                info['white_bal'] = int(white_bal)

            if text == "Taken:":
                date_taken = b.next_sibling
                info['date_taken'] = date_taken.lstrip()

            if text == "Location:":
                location = b.next_sibling
                info['location'] = location.lstrip()

            if text == "Tags:":
                tags = list(b.next_siblings)
                info['tags'] = tags

            info['url'] = item_url

            if text == "Categories:":
                categories = []
                categories_group = [x for x in list(b.next_siblings) if x and ', ' not in x]
                for c in categories_group:
                    try:
                        categories.append(c.contents[0])
                    except AttributeError:
                        pass

                info['keywords'] = categories

            if text == "Tags:":
                tags = []
                tags_group = [x for x in list(b.next_siblings) if x and ', ' not in x]
                for c in tags_group:
                    try:
                        tags.append(c.contents[0])
                    except AttributeError:
                        pass

                info['tags'] = tags

        full_href = None

        for button_container in download_buttons:

            for button in button_container.children:

                try:
                    href = button.attrs['href']
                    # Prevent things like 24k. lol
                    if '_%s' % res in href:
                        full_href = href

                except KeyError:
                    pass

        # DO DOWNLOAD HERE
        download_it(res, full_href, download_dir, info)

    print('---------------------------')


if __name__ == "__main__":

    # Location of output
    main('C:\\_tmp\\hdrihaven_metadata')
