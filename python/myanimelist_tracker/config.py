# Define the global paths here

import getpass
myanimelist_url = 'http://myanimelist.net/anime/season'

if 'centos' in getpass.getuser():
    base_path = '/mnt/Dropbox/lumacode/anime_tracker'
else:
    base_path = '/home/centos/anime_tracker'


data_directory = 'data'
