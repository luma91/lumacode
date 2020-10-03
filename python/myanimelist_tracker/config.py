# Define the global paths here

import platform
myanimelist_url = 'http://myanimelist.net/anime/season'

if 'Linuxbox' in platform.node():
    base_path = '/mnt/Dropbox/lumacode/anime_tracker'
else:
    base_path = '/home/centos/anime_tracker'


data_directory = 'data'
