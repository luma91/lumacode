
""" Main Script for loading Citadel Functions """

from lumacode.citadel import functions


def main():
    discord = functions.make_thread('discord_bot/discord_bot.py')
    discord.start()

    plex = functions.make_thread('nyaa/plex_sync.py')
    plex.start()

    nyaa = functions.make_thread('nyaa/nyaa_headless.py')
    nyaa.start()

    lifx = functions.make_thread('lifx/lifx_web.py')
    lifx.start()


if __name__ == "__main__":
    main()
