import threading
import time

import nyaa_downloader


def main_loop():

    while True:

        try:

            # Run the scan
            nyaa_downloader.main('nas')
            print('scan complete. will run again in 1 hour')

        except Exception as e:
            print(e)

        # Sleep for an hour
        time.sleep(3600)


t = threading.Thread(target=main_loop)
t.start()
