
import os
import time

import discord


# Check for New Episodes
async def check_new_episodes(client, channel):

    from lumacode.nyaa import plex_sync
    base_directory = "/mnt/Media/.temp"
    plex_directory = "/mnt/Media/Anime"
    download_dir = os.path.join(base_directory, "qbittorrent", "completed")

    while True:

        # Check for Episodes
        file_list = os.listdir(download_dir)
        file_list.sort()
        file_list_new = []

        # Check if new episodes available!
        if len(file_list) > 0:
            for f in file_list:
                if f.endswith('.mkv'):
                    file_list_new.append(f)

            # Initial wait period in case files are incomplete.
            time.sleep(10)

            if len(file_list_new) > 0:
                response = "@everyone New Episodes Available!\n%s" % '\n'.join(file_list_new)

                # Prevent Repeating Messages
                if (x for x in client.cached_messages if response not in str(x.content)):

                    # All Clear, Let's run the code!
                    plex_sync.run_sync(plex_directory, base_directory)  # Force Plex Sync
                    print('Sending: %s\n' % response)

                    # Send a message
                    await channel.send(response)

        # Reduce I/O on NAS.
        time.sleep(30)


def send_message(message):

    client = discord.Client()

    @client.event
    async def on_ready():

        channel = client.get_channel(channel_id)

        await channel.send(message)
        await client.logout()

    client.run(token)
