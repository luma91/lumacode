# Define the global paths here

import socket
myanimelist_url = 'http://myanimelist.net/anime/season'

local = True
local_addresses = ['raspberrypi', 'Linuxbox']

if any(x for x in local_addresses if x in socket.gethostname()):
    base_path = '/mnt/Dropbox/python/anime_tracker'
else:
    base_path = '/home/centos/anime_tracker'
    local = False

log_directory = 'log'
data_directory = 'data'
