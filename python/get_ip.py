# This example requires the requests library be installed.  You can learn more
# about the Requests library here: http://docs.python-requests.org/en/latest/
# https://ip-api.com/docs/api:batch#test


import os
import platform
import logging
import urllib.request
import subprocess
import datetime
import requests
import time
import json
import luma_log
from bs4 import BeautifulSoup

host_name = platform.node()
storage_location = '/mnt/tmp/ip_addr/'
ip_file = '%s.wan-ip.txt' % host_name.lower()

# Get Logger
logger = luma_log.main(__file__)


# Define Error
class GetIpError(Exception):
    pass


def get_location(method, ip):

    # Not very reliable...
    if method == 1:
        location_data = requests.post('http://ip-api.com/batch?fields=status,message,country,countryCode,region,regionName,city,zip,lat,lon,timezone,isp,org,as,query','[{"query": "' + ip + '", "fields": "city,country,countryCode,query"}]').text
        location_data_processed = json.loads(location_data)
        location = location_data_processed[0]['country']

        return location

    # More robust, but still fails sometimes
    elif method == 2:
        location = None
        url = 'https://ipgeolocation.io/ip-location/' + ip
        user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'
        request = urllib.request.Request(url, headers={'User-Agent': user_agent})
        response = urllib.request.urlopen(request)
        soup = BeautifulSoup(response, 'html.parser')
        elements = soup.find_all('td')
        num = 0

        for element in elements:
            content = element.contents

            if 'Country Name' in content:
                location = elements[num + 1].contents[0]

            num += 1

        return location


def get_ip(method):

    if method == 1:
        ip = requests.get('https://api.ipify.org').text

        if len(ip) < 20:
            return ip

        else:
            raise GetIpError("Cannot get IP Address.")

    elif method == 2:
        url = 'https://whatismyipaddress.com/ip-lookup'
        user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'
        request = urllib.request.Request(url, headers={'User-Agent': user_agent})
        response = urllib.request.urlopen(request)
        soup = BeautifulSoup(response, 'html.parser')
        element = soup.find('input', type='TEXT')
        content = element.get('value')
        ip = content
        logging.info('My public IP address is: %s' % ip)

        return ip


def write_to_disk(ip, location):

    try:

        if len(ip) > 20:
            ip = 'Unknown'

        if len(location) > 20:
            location = 'Unknown'

        now = datetime.datetime.now()
        data_to_write = '{"time": "%s", "ip": "%s", "country": "%s"}' % (now, ip, location)
        logger.info('writing %s to disk.' % data_to_write)
        f = open(os.path.join(storage_location, ip_file), 'w+')
        f.write(data_to_write)
        f.close()
        time.sleep(10)

    # Failed to write to file. Try re-mounting drive?
    except Exception as e:
        logging.exception(e)
        cmd = ['/bin/bash', '-c', 'sudo mount -av']
        subprocess.run(cmd)
        time.sleep(30)


# Main Function
def ip_check():

    logger.info("Starting IP Checker")
    while True:

        ip = None
        location = None

        # --- Get IP ---
        for _ in range(100):

            try:
                try:
                    ip = get_ip(1)
                    logger.info('My public IP address is: %s' % ip)

                except Exception as e:
                    logger.error(e)
                    ip = get_ip(2)

                break

            except Exception as e:
                logger.error(e)
                pass

        # --- Get Country ---
        # Method 1

        if ip:
            for _ in range(100):

                try:
                    try:
                        location = get_location(1, ip)
                        logger.info('Used Method 1. Location: %s' % location)

                    except Exception as e:
                        logger.error(e)
                        time.sleep(5)

                        location = get_location(2, ip)
                        logger.info('Used Method 2. Location: %s' % location)

                    break

                except Exception as e:
                    logger.error('Still Failing!\n\n%s' % e)
                    location = 'Unknown'

                    # Write the unknown state to disk
                    write_to_disk(ip, location)
                    pass

        # ----------------

        write_to_disk(ip, location)
        time.sleep(120)


if __name__ == "__main__":
    ip_check()
