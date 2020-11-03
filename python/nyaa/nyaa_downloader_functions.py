import urllib.request
import os
import platform
from xml.dom import minidom
import config

platform_os = platform.platform()
base_path = os.path.dirname(__file__)


def run_scan(logger, show):

    logger.info("Scanning: " + show['name'])
    show_filtered = str(show['name']).replace(" ", "+")
    url = (
            config.website +
            "&q=" + show_filtered +
            "+" + str(show['subgroup']) +
            "+" + config.video_quality +
            config.flags
    )

    # Exception for Sub HD.
    if "no" in show['fullhd'].lower():
        url = (config.website + "&q=" + show_filtered + "+" + str(show['subgroup']) + "+" + config.flags)

    logger.info(url)
    page = urllib.request.urlopen(url)
    page_data = page.read()
    xml_doc = minidom.parseString(page_data)
    item_list = xml_doc.getElementsByTagName("item")

    added_torrents = os.listdir(config.added_dir)

    title_list = []
    link_list = []
    seeders_list = []
    size_list = []
    filtered_list = []

    for item in item_list:
        title = item.getElementsByTagName("title")[0].childNodes[0].data
        link = item.getElementsByTagName("link")[0].childNodes[0].data
        seeders = item.getElementsByTagName("nyaa:seeders")[0].childNodes[0].data
        size = item.getElementsByTagName("nyaa:size")[0].childNodes[0].data

        # Check for ignore flags in title
        if any(x for x in config.filter_flags if x in title) is False:

            # Check for existing torrent files, skip if existing, then Download latest
            if any(x for x in added_torrents if title + ".torrent" in x) is False:
                title = title.replace(" / ", " - ")  # Fix for stupid groups.
                title_list.append(title)
                link_list.append(link)
                seeders_list.append(seeders)
                size_list.append(size)

        else:
            filtered_list.append(title)

    parsed_shows_list = zip(title_list, link_list, seeders_list, size_list)
    return parsed_shows_list, filtered_list


def download_torrents(logger, download_list):

    # Download Torrent Files
    for title in download_list:

        try:
            torrent_file = os.path.join(config.torrent_dir, title + ".torrent")
            urllib.request.urlretrieve(download_list[title], torrent_file)
            logger.info("Downloading: %s" % title)

        except Exception as e:
            logger.error(e)
