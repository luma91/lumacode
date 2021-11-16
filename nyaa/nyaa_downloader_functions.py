
import os
import platform
import urllib.request
import ssl

from lumacode.nyaa import config
from xml.dom import minidom
from lumacode import luma_log

logger = luma_log.main(__file__)
platform_os = platform.platform()
base_path = os.path.dirname(__file__)

# SSL
_create_unverified_https_context = ssl._create_unverified_context
ssl._create_default_https_context = _create_unverified_https_context


def check_for_episodes(subgroup, show_name, is_1080p='yes'):

    show_name = show_name.lstrip().rstrip()

    logger.info("Scanning: %s by subgroup: %s" % (show_name, subgroup))
    show_filtered = str(show_name).replace(" ", "+")
    url = (
            config.website +
            "&q=" + show_filtered +
            "+" + str(subgroup) +
            "+" + config.video_quality +
            config.flags
    )

    # Exception for Sub HD.
    if "no" in is_1080p.lower():
        url = (config.website + "&q=" + show_filtered + "+" + str(subgroup) + "+" + config.flags)

    logger.info(url)

    url = url.replace(' ', '+')
    page = urllib.request.urlopen(url)
    page_data = page.read()
    xml_doc = minidom.parseString(page_data)
    item_list = xml_doc.getElementsByTagName("item")

    # Get torrents already on disk, filtered by show name
    added_torrents = [x for x in os.listdir(config.added_dir) if show_name.lower() in x.lower()]
    added_torrents.sort()

    # Do the scan
    filtered_list = []
    title_list, link_list = [], []
    for item in item_list:
        title = item.getElementsByTagName("title")[0].childNodes[0].data
        link = item.getElementsByTagName("link")[0].childNodes[0].data

        # Check for ignore flags in title
        if any(x for x in config.filter_flags if x in title) is False:

            # Hack for episodes that have this weird issue.
            if '(' in title:
                title = title.split('(')
                if len(title) > 1:
                    title = title[0].rstrip()

            if any(x for x in added_torrents if title.lower() in x.lower()) is False:
                title = title.replace(" / ", " - ")  # Fix for stupid groups.
                title_list.append(title)
                link_list.append(link)

        else:
            filtered_list.append(title)

    parsed_shows_list = zip(title_list, link_list)
    return parsed_shows_list, filtered_list


def download_torrents(download_list):

    # Download Torrent Files
    for title in download_list:

        try:
            torrent_file = os.path.join(config.torrent_dir, title + ".torrent")
            urllib.request.urlretrieve(download_list[title], torrent_file)
            logger.info("Downloading: %s to: %s" % (title, torrent_file))

        except Exception as e:
            logger.error(e)


if __name__ == "__main__":
    parsed, filtered, = check_for_episodes('[Anime Time]', 'Komi-san')
    for ep in parsed:
        print('we are downloading: %s' % ep[0])
