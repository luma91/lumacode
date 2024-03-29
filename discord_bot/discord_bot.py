# https://discordpy.readthedocs.io/en/latest/
# https://discordpy.readthedocs.io/en/latest/faq.html#how-do-i-send-a-message-to-a-specific-channel

import os
import random
import sys

import discord
import pyHS100
from wakeonlan import send_magic_packet

from lumacode.discord_bot import bot_functions, constants
from lumacode.lifx import lifx, lifx_presets
from lumacode import luma_log, get_smartdevices, receiver


import logging
logging.basicConfig(level=logging.ERROR)

# Get Logger
logger = luma_log.main(__file__)

# Bot Stuff
python_bin = sys.executable
script_path = os.path.split(__file__)[0]
color = [.3, .4, 0, 0.5]

base_path = os.path.dirname(__file__)


# Primary Bot Functions
def discord_bot():

    client = discord.Client()

    # Keywords to trigger the bot
    welcome_phrases = ['hello', 'hey', 'hi', 'howdy', 'yo', 'sup']
    goodbye_phrases = ['cya', 'bye', 'ciao', 'goodnight']
    nice_words = ['love', 'like', 'best', 'nice', 'happy', 'hug']
    naughty_words = ['hate', 'fuck', 'screw', 'shit', 'crap', 'bastard', 'cunt', 'pussy', 'dick', 'ass',
                     'dumb', 'stupid', 'bitch', 'hate', 'dislike', 'suck']

    def turn_on_everything():

        # Turn on Lights
        try:
            lights = lifx.get_lights(method="CLOUD")
            for x in lights:
                x.power_on()

        except Exception as e:
            logger.error(e)

        # Turn Off Camera
        try:
            kitchen_camera = pyHS100.SmartPlug(get_smartdevices.address(category='smartplugs', name='kitchen_camera'))
            living_room_camera = pyHS100.SmartPlug(get_smartdevices.address(category='smartplugs', name='living_room_camera'))
            kitchen_camera.turn_off()
            living_room_camera.turn_off()

        except Exception as e:
            logger.error(e)

        # Turn on PC
        try:
            send_magic_packet('04.D9.F5.7C.0D.B3', '68.05.CA.9F.00.49')  # Turn on PC

        except Exception as e:
            logger.error(e)

        # Turn on Receiver
        try:
            rec = receiver.Main()
            rec.power_on()

        except Exception as e:
            logger.error(e)

    @client.event
    async def on_ready():
        logger.info("Bot Connected.")

        # channel = client.get_channel(channel_id)
        # Commented out to prevent spam
        # response = "@everyone I'm Alive!"
        # await channel.send(response)

    @client.event
    async def on_message(message):

        # Make sure we're on the right channel
        if str(message.channel) != "general":
            return

        if message.author is not client.user:

            logger.info('user: %s msg: %s' % (message.author, message.content))

            message_content = message.content.lower()
            response = None

            if "!logout" in message_content or "!exit" in message_content:
                response = "bye..."
                await message.channel.send(response)
                await client.logout()
                sys.exit()

            # Clear all messages // Not Currently Supported?
            elif "!clear" in message_content:
                await message.channel.purge()

            # Respond to a Hello!
            elif any(word == message_content for word in welcome_phrases):
                response = 'Welcome ' + message.author.mention + '!'

            # Respond to a Goodbye!
            elif any(word == message_content for word in goodbye_phrases):
                response = 'Bye ' + message.author.mention + ' have a nice day!'

            # Respond to my Name!
            elif constants.bot_name.lower() in message_content or str(constants.bot_id) in message_content:

                # Generic response
                response = 'Hey ' + message.author.mention + ', What\'s up?'

                # Naughty words?!
                if any(word in message_content for word in naughty_words):
                    random_number = random.randrange(5)

                    if random_number == 0:
                        response = "that's not very nice.... " + message.author.mention

                    if random_number == 1:
                        response = "why would you say that to me? " + message.author.mention

                    if random_number == 2:
                        response = ":slight_frown:"

                    if random_number == 3:
                        response = "Im sad... :sob:"

                    if random_number == 4:
                        response = "please don't talk to me like that!"

                    if random_number == 5:
                        response = "please stop...."

                # Nice Words?
                if any(word in message_content for word in nice_words):
                    random_number = random.randrange(5)

                    if random_number == 0:
                        response = "Awwww!"

                    if random_number == 1:
                        response = "Thankyou!"

                    if random_number == 2:
                        response = "Your so kind!"

                    if random_number == 3:
                        response = "Yay!!!"

                    if random_number == 4:
                        response = ":blush:"

                    if random_number == 5:
                        response = ":heart_eyes:"

            # //////////////////////////////////////////////////////////////////
            # Smart Home Stuff!
            else:
                if any(user in str(message.author) for user in constants.trusted_users):

                    # Get Smart Devices
                    kitchen_camera = pyHS100.SmartPlug(get_smartdevices.address(category='smartplugs', name='kitchen_camera'))
                    living_room_camera = pyHS100.SmartPlug(get_smartdevices.address(category='smartplugs', name='living_room_camera'))
                    subwoofer = pyHS100.SmartPlug(get_smartdevices.address(category='smartplugs', name='subwoofer'))
                    rec = receiver.Main()

                    # Turn on everything!
                    if any(x for x in ["turn on everything", "home", "awake"] if x in message_content):
                        turn_on_everything()
                        response = "I have turned everything on!"

                    elif "headphones" in message_content:

                        try:
                            rec.power_on()
                            rec.send_command(receiver.SPEAKER_OFF)
                            rec.set_input('pc')
                            response = "Don't type too loud, thanks."

                        except Exception as e:
                            logger.exception(e)
                            response = "I could not do this. sorry... please try again!"

                    elif "bed" in message_content:

                        try:
                            rec.power_off()
                            response = "Enjoy your anime!"

                        except Exception as e:
                            logger.exception(e)
                            response = "I could not do this. sorry...  please try again!"

                        lights = lifx.get_lights(method="CLOUD")
                        for x in lights:
                            x.power_off()

                        subwoofer.turn_off()

                    elif "pc" in message_content:

                        try:
                            rec.power_on()
                            rec.send_command(receiver.SPEAKER_B)
                            rec.set_input('pc')
                            response = "Enjoy your chatting to rose..."

                        except Exception as e:
                            logger.exception(e)
                            response = "I could not do this. sorry...  please try again!"

                    elif "tv" in message_content:

                        try:
                            rec.power_on()
                            rec.send_command(receiver.SPEAKER_A)
                            rec.set_input('pc')
                            subwoofer.turn_on()
                            response = "Enjoy your anime!"

                        except Exception as e:
                            logger.exception(e)
                            response = "I could not do this. sorry...  please try again!"

                        lifx_presets.set_preset('movie', 'living_room')

                    elif "camera" in message_content:

                        if "on" in message_content:
                            response = "Security systems activated!"
                            kitchen_camera.turn_on()
                            living_room_camera.turn_on()

                        if "off" in message_content:
                            response = "You may now do your dirty deeds..."
                            kitchen_camera.turn_off()
                            living_room_camera.turn_off()

                    elif "mute" in message_content:
                        rec.mute()
                        response = "Okay I've toggled the mute button!"

                    elif "speakers" in message_content:

                        if "on" in message_content:
                            response = "Okay. I'll turn it on."
                            rec.power_on()

                        elif "off" in message_content:
                            response = "Okay, I'll turn it off."
                            rec.power_off()

                    # Lights On/Off
                    elif "lights" in message_content:

                        # Study
                        if "study" in message_content:

                            if "on" or "off" in message_content:
                                study_lights = lifx.get_lights(group='Study', method="CLOUD")

                                if "on" in message_content:
                                    for x in study_lights:
                                        x.power_on()
                                    response = "Study lights on!"

                                if "off" in message_content:
                                    for x in study_lights:
                                        x.power_off()
                                    response = "Study lights off!"

                            presets = lifx_presets.load_presets('Study')
                            for preset in presets:

                                # Exact Match (example: study lights preset_01)
                                match = 0
                                split_message = message_content.split()
                                if len(split_message) == 3:
                                    if preset.lower() == split_message[2].lower():
                                        lifx_presets.set_preset(preset, group="Study")
                                        match = 1

                                # Any Match
                                if match == 0:
                                    if preset.lower() in message_content:
                                        lifx_presets.set_preset(preset, group="Study")

                        # Living Room
                        elif 'living' in message_content:

                            if "on" or "off" in message_content:
                                living_lights = lifx.get_lights(group='Living Room', method="CLOUD")

                                if "on" in message_content:
                                    response = "Let there be light!"
                                    for x in living_lights:
                                        x.power_on()

                                elif "off" in message_content:
                                    response = "Enjoy the darkness...."
                                    for x in living_lights:
                                        x.power_off()

                            presets = lifx_presets.load_presets('Living Room')
                            for preset in presets:

                                # Exact Match (example: study lights preset_01)
                                match = 0
                                split_message = message_content.split()
                                if len(split_message) == 3:
                                    if preset.lower() == split_message[2].lower():
                                        lifx_presets.set_preset(preset, group="Living Room")
                                        match = 1

                                # Any Match
                                if match == 0:
                                    if preset.lower() in message_content:
                                        lifx_presets.set_preset(preset, group="Living Room")

                        # All Lights
                        else:

                            lights = lifx.get_lights(method="CLOUD")

                            if "on" in message_content:
                                response = "Let there be light!"
                                lights.power_on()

                            elif "off" in message_content:
                                response = "Enjoy the darkness...."
                                lights.power_off()

                    # Receiver Volume
                    elif ("make" in message_content) or ("turn" in message_content):

                        if ("loud" in message_content) or ("up" in message_content):
                            rec.set_volume('121')
                            response = "Okay, I've turned it up!"

                        elif ("quiet" in message_content) or ("down" in message_content):
                            rec.set_volume('091')
                            response = "Okay I've turned it down!"

            # ----------------------------------------------------------
            # ----------------------------------------------------------

            # Send Message
            if response is not None:
                await message.channel.send(response)
                logger.info('Replying with: %s\n' % response)

            # ----------------------------------------------------------
            # ----------------------------------------------------------

        else:
            return

    # Run
    client.run(constants.token)


# Run
if __name__ == "__main__":

    print("Running Discord Bot")
    discord_bot()
