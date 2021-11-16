
import os
import platform
import sys

platform_os = platform.platform()
website = "https://nyaa.si/?page=rss"
flags = "&c=1_2&f=0"  # These do something, I'm totally sure of it...
video_quality = "1080p"
filter_flags = ["mini", "batch", "batched", "NoobSubs", "VRV", "Where", "Hardsub", "60FPS"]  #, "HEVC"

# Paths
base_directory = '/mnt/Media/.temp'
plex_directory = '/mnt/Media/Anime'

# Windows
if "windows" in platform_os.lower():
    plex_directory = 'M:/Anime'
    base_directory = 'M:/.temp'

show_database = os.path.join(base_directory, 'show_database.json')
torrent_dir = os.path.join(base_directory, 'qbittorrent', 'watch')
added_dir = os.path.join(base_directory, 'qbittorrent', 'added')
download_dir = os.path.join(base_directory, 'qbittorrent', 'completed')

# For the Logging
base_path = os.path.dirname(__file__)
sys.path.append(base_path)
sys.path.append(os.path.join(base_path, '..'))
