
import os
import time
import threading

from lumacode.nyaa import plex_sync, config


def main_loop(wait):

    while True:

        # Check for MKV files.
        file_list = os.listdir(config.download_dir)
        if len(file_list) > 0 and (x for x in file_list if '.mkv' in x):
            print('found an MKV file. running sync in 15 seconds.')
            time.sleep(15)  # Wait 15 seconds
            plex_sync.run_sync(send_msg=True)

        # Wait until next cycle
        time.sleep(wait)


def main(wait=60):
    thread = threading.Thread(target=main_loop, args=(wait,))
    thread.start()


if __name__ == "__main__":
    main()
