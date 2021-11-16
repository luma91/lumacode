
# http://theautomatic.net/2019/01/19/scraping-data-from-javascript-webpage-python/
# https://docs.python-requests.org/projects/requests-html/en/latest/

import urllib.request
from requests_html import HTMLSession
from bs4 import BeautifulSoup

agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) ' \
        'Chrome/35.0.1916.47 Safari/537.36'


def retry_on_failure(default_value='', attempts=10):

    """
    This will allow us to retry without crashing the entire program.

    """

    def decorator(func):

        def new_func(*args, **kwargs):

            for _ in range(attempts):
                try:
                    return func(*args, **kwargs)

                except Exception as e:

                    print('error: %s. attempt %s of %s' % (e, _ + 1, attempts))
                    continue

        return new_func

    return decorator


@retry_on_failure()
def do_soup(session, link, element):

    # Use the object above to connect to needed webpage
    contents = session.get(link)

    # Run JavaScript code on webpage
    contents.html.render()

    grid_element = contents.html.find(element)[0]
    return BeautifulSoup(grid_element.html, "lxml")


@retry_on_failure()
def no_soup(session, link):

    # Use the object above to connect to needed webpage
    contents = session.get(link)

    # Run JavaScript code on webpage
    contents.html.render()

    return contents


def main():

    base_url = "https://polyhaven.com"
    url = base_url + '/textures'

    # create an HTML Session object
    session = HTMLSession()

    soup = do_soup(session, url, '.Grid_grid__k8fvr')
    elements = soup.find_all('a', attrs={'class': 'GridItem_gridItem__K7DK-'})
    links = [base_url + x.attrs['href'] for x in elements]

    for link in links:

        print(link)

        # Download_downloadBtn__2EdxD
        content = no_soup(session, link)
        print(content)

        script = """
            window.onload = function(){
                console.log('test');
                var a = document.getElementsByClassName('Download_downloadBtn__2EdxD');
                a.click();
            }
        """

        response = content.html.render(sleep=2, timeout=10000, script=script, keep_page=True)
        print(response)

        # Testing
        break

    # Return number of items
    print('%s items.' % len(links))


if __name__ == "__main__":
    main()
