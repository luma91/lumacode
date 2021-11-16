
import json
import os
import shutil
import subprocess
import time
import threading

from lumacode.nyaa import config
from lumacode import luma_log
from lumacode.discord_bot import bot_functions

# Get Logger
logger = luma_log.main(__file__)
logger.info('Plex Sync Initialized.')


def has_numbers(input_string):

    for char in input_string:
        if char.isdigit():
            return char


def remove_torrent():

    # TODO: Deluge Function. needs to be repurposed for QBitTorrent

    cmd = ['deluge-console', '"connect 192.168.0.238 andrew pass ; info"']
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
    _stdout, _stderr = proc
    print(_stdout, _stderr)


def copy_file(src, dst, ep):

    try:
        shutil.copy2(src, dst)
        logger.info(">>> Moved %s!\n" % ep)

    except Exception as e:

        print(e)
        logger.error(e)
        logger.warning("Cannot move file: " + src + " skipping...")
        logger.warning("src: %s dst: %s ep: %s" % (src, dst, ep))


def move_file(src, dst, ep):

    try:
        # if os.path.exists(dst) is False:
        shutil.move(src, dst)
        logger.info(">>> Moved %s!\n" % ep)

        # else:
        #    print("Warning: %s exists! Cannot Move!" % dst)

    except Exception as e:
        print(e)
        logger.error(e)
        logger.warning("Cannot move file: " + src + " skipping...")
        logger.warning("src: %s dst: %s ep: %s" % (src, dst, ep))


def run_sync(send_msg=False):

    # Read database
    with open(config.show_database, "r") as f:
        database = json.load(f)

    logger.info("Running Plex Sync...\n\n")
    files = []
    episodes_to_transfer = []

    # Build a list of new available episodes
    for f in os.listdir(config.download_dir):
        files.append(f)

    # Check against shows already in database (for direct matching)
    for show in database:

        for f in files:

            if f not in episodes_to_transfer:

                # Exact Match (7 letters or more)
                if show['name'] in f and len(show['name']) > 7:

                    src = os.path.join(config.download_dir, f)
                    dst = os.path.join(config.plex_directory, show['name'], f)

                    if os.path.exists(os.path.join(config.plex_directory, show['name'])):
                        episodes_to_transfer.append(f)
                        logger.info("EXACT MATCH: \"%s\"\nSource: %s \nDestination: %s\n" % (show['name'], src, dst))

                        # TODO: Replace delug function with qbittorrent function!
                        # deluge_functions.remove_completed_torrents()

                        time.sleep(10)
                        move_file(src, dst, f)

                        # Send discord message
                        if send_msg:
                            bot_functions.send_message('new episode available for: %s' % f)

    # Episodes with nowhere to go!
    logger.info("Checking for stragglers...")

    # Clear and rescan for stragglers
    files = []
    plex_shows = []

    for f in os.listdir(config.download_dir):
        files.append(f)

    # Build a list of "shows" from PLEX.
    for d in os.listdir(config.plex_directory):
        if "@eaDir" not in d:
            plex_shows.append(d)

    # Check new episode names against shows in PLEX.
    for f in files:

        if f not in episodes_to_transfer:
            logger.info("Running straggler check on %s\n" % f)
            found_match = 0

            for show in plex_shows:
                split_names = show.split(' ')

                for x in split_names:

                    # Keep checking until we have a match, or run out of words.
                    if found_match == 0:

                        # Block Common Words (i.e. HD, 1080p, BD, etc..)
                        common_words = ["no", "a", "to", ".", "in", "ni", "wa", "yo", "ga", "720p", "1080p", "BD", '-', '[', ']', 'x264', 'flac']
                        if x not in common_words:

                            # Prevent Sub Groups from being Matched
                            if '[' not in x or ']' not in x:

                                # If a word is matched (that is 4 characters or more)
                                if x in f and len(x) >= 4:

                                    # Simple check for season number (i.e. Chihiyafuru S3)
                                    season_number = has_numbers(show)

                                    if season_number:
                                        logger.info("SHOW: %s  NUMBER: %s" % (show, season_number))

                                    if season_number:
                                        if season_number not in f:
                                            continue  # Skip because not right season

                                    logger.info("MATCH FOUND: \"%s\" in \"%s\" " % (x, f))
                                    src = os.path.join(config.download_dir, f)
                                    dst = os.path.join(config.plex_directory, show, f)
                                    logger.info("Source: %s \nDestination: %s\n" % (src, dst))

                                    # TODO: Replace delug function with qbittorrent function!
                                    # deluge_functions.remove_completed_torrents()

                                    time.sleep(10)
                                    move_file(src, dst, f)
                                    found_match = 1

                                    # Send discord message
                                    if send_msg:
                                        bot_functions.send_message('new episode available for: %s\ncopied to %s' % (f, dst))

            if found_match == 0:
                logger.warning("Could not find anywhere for the file to go :(")


def main_loop(wait):

    print('running plex sync')

    while True:

        # Check for MKV files.
        file_list = os.listdir(config.download_dir)
        if len(file_list) > 0 and (x for x in file_list if '.mkv' in x):
            print('found an MKV file. running sync in 15 seconds.')
            time.sleep(15)  # Wait 15 seconds
            run_sync(send_msg=True)

        # Wait until next cycle
        time.sleep(wait)


def main(wait=60):
    thread = threading.Thread(target=main_loop, args=(wait,))
    thread.start()


if __name__ == "__main__":
    main()
