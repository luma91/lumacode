import os
import shutil
import json
import luma_log

# Get Logger
logger = luma_log.main(__file__)
logger.info('Plex Sync Initialized.')


exceptions = [
    "no", "a", "to", ".", "in", "ni", "wa", "yo", "ga", "720p", "1080p", "BD", '-', '[', ']', 'x264', 'flac'
]


def has_numbers(input_string):

    for char in input_string:
        if char.isdigit():
            return char


def move_file(src, dst, ep):

    try:
        shutil.move(src, dst)
        logger.info(">>> Moved %s!\n" % ep)

    except Exception as e:
        logger.error(e)
        logger.warning("Cannot move file: " + src + " skipping...")
        logger.warning("src: %s dst: %s ep: %s" % (src, dst, ep))


def run_sync(plex_directory, base_directory):

    download_dir = os.path.join(base_directory, 'transmission/completed')
    show_database = os.path.join(base_directory, "show_database.json")

    with open(show_database, "r") as f:
        database = json.load(f)

    logger.info("Running Plex Sync...\n\n")
    new_episodes = []
    episodes_to_transfer = []

    for f in os.listdir(download_dir):
        new_episodes.append(f)

    for show in database:

        for ep in new_episodes:

            if ep not in episodes_to_transfer:

                # Exact Match (7 letters or more)
                if show['name'] in ep and len(show['name']) > 7:

                    src = os.path.join(download_dir, ep)
                    dst = os.path.join(plex_directory, show['name'], ep)

                    if os.path.exists(os.path.join(plex_directory, show['name'])):
                        episodes_to_transfer.append(ep)
                        logger.info("EXACT MATCH: \"%s\"\nSource: %s \nDestination: %s\n" % (show['name'], src, dst))
                        move_file(src, dst, ep)

    # Episodes with nowhere to go!
    logger.info("Checking for stragglers...")

    # Clear and rescan for stragglers
    new_episodes = []
    shows = []

    for f in os.listdir(download_dir):
        new_episodes.append(f)

    for d in os.listdir(plex_directory):
        if "@eaDir" not in d:
            shows.append(d)

    for ep in new_episodes:

        if ep not in episodes_to_transfer:
            logger.info("Running straggler check on %s\n" % ep)
            found_match = 0

            for show in shows:  # Shows being folders in PLEX Directory
                split_names = show.split(' ')

                for x in split_names:

                    if found_match is 0:

                        # Block Common Words
                        if x not in exceptions:

                            # Prevent Sub Groups from being Matched
                            if '[' or ']' not in x:

                                # If a word is matched (that is 4 characters or more)
                                if x in ep and len(x) >= 4:

                                    # Simple check for season number (i.e. Chihiyafuru S3)
                                    season_number = has_numbers(show)

                                    if season_number:
                                        logger.info("SHOW: %s  NUMBER: %s" % (show, season_number))

                                    if season_number:
                                        if season_number not in ep:
                                            continue  # Skip because not right season

                                    logger.info("MATCH FOUND: \"%s\" in \"%s\" " % (x, ep))
                                    src = os.path.join(download_dir, ep)
                                    dst = os.path.join(plex_directory, show, ep)
                                    logger.info("Source: %s \nDestination: %s\n" % (src, dst))
                                    move_file(src, dst, ep)
                                    found_match = 1

            if found_match == 0:
                logger.warning("Could not find anywhere for the file to go :(")

    logger.info("Plex Sync Finished.\n")


if __name__ == "__main__":
    run_sync("/mnt/Media/Anime", "/mnt/ds918-Media/.temp")
