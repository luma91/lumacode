# Bot Functions v0.1
import os
import sys
import time
import discord


# Check for New Episodes
async def check_new_episodes(client, channel):

    sys.path.append(os.path.join(os.path.dirname(__file__), '../nyaa'))
    import plex_sync
    base_directory = "/mnt/Media/.temp"
    plex_directory = "/mnt/Media/Anime"
    download_dir = os.path.join(base_directory, "transmission/completed")

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
                check = False

                # Prevent Repeating Messages
                for i in client.cached_messages:
                    if response == str(i.content):
                        check = True

                # All Clear, Let's run the code!
                if check is False:
                    print('Sending: %s\n' % response)
                    await channel.send(response)
                    plex_sync.run_sync(plex_directory, base_directory)  # Force Plex Sync

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
