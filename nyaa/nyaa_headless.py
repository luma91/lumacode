
import json
import threading
import time

from lumacode.nyaa import config, nyaa_downloader_functions
from lumacode import luma_log

logger = luma_log.main(__file__)


def run_scan():

    # Open database and check for shows
    with open(config.show_database, "r") as f:
        shows = json.load(f)

    print('checking %s for torrents.' % config.added_dir)
    download_list = {}

    for show in shows:
        parsed_shows_list, filtered_list = nyaa_downloader_functions.check_for_episodes(
            show['subgroup'],
            show['name'],
            show['fullhd']
        )

        for title, link in parsed_shows_list:

            if str(show['name']).lower() in title.lower():
                logger.info("Found an episode for %s!" % title)
                download_list.update({title: link})

        # Print out filtered shows
        for title in filtered_list:
            f = [x for x in config.filter_flags if x in title]
            logger.debug('omitting %s due to filter: %s' % (title, ''.join(f)))

    logger.info("Scan Complete!")

    if len(download_list) > 0:
        nyaa_downloader_functions.download_torrents(download_list)

    else:
        logger.info("No new episodes found")


def main_loop():

    while True:

        try:

            # Run the scan
            run_scan()
            print('scan complete. will run again in 1 hour')

        except Exception as e:
            print(e)

        # Sleep for an hour
        time.sleep(3600)


t = threading.Thread(target=main_loop)
t.start()
