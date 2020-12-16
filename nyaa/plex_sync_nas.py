
import os
from lumacode.nyaa import plex_sync

base_directory_nas = "/volume1/Media/.temp/deluge"
plex_directory = "/volume1/Media/Anime"
download_dir = os.path.join(base_directory_nas, "completed")
plex_sync.run_sync(plex_directory, download_dir)
