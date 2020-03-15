# https://discordpy.readthedocs.io/en/latest/
# https://discordpy.readthedocs.io/en/latest/faq.html#how-do-i-send-a-message-to-a-specific-channel

import discord
import random
import bot_functions
import subprocess
import sys
import threading
import os
import time
import json

base_path = os.path.dirname(__file__)
sys.path.append(os.path.join(base_path, '..'))

# Bot Stuff
python_bin = sys.executable
script_path = os.path.split(__file__)[0]
color = [.3, .4, 0, 0.5]

with open(os.path.join(base_path, 'bot_data.json')) as f:
    bot_data = json.loads(f.read())

# Bot Data
# Define this in bot_data.json
client_secret = bot_data['client_secret']
client_id = bot_data['client_id']
token = bot_data['token']
bot_name = bot_data['bot_name']
username = bot_data['username']
bot_id = bot_data['bot_id']
channel_id = bot_data['channel_id']
trusted_users = bot_data['trusted_users']


# Check For Episodes
def check_new_episodes():

    client = discord.Client()

    @client.event
    async def on_ready():
        print("Watching Episodes.")
        channel = client.get_channel(channel_id)

        # Check for new episodes
        await bot_functions.check_new_episodes(client, channel)

    @client.event
    async def on_message(message):

        message_content = message.content.lower()
        if "!logout" in message_content:
            await client.logout()
            sys.exit()

    client.run(token)


# Primary Bot Functions
def discord_bot():

    import receiver
    import lifx
    import lifx_presets
    import wifi370
    import pyHS100
    from wakeonlan import send_magic_packet
    import get_smartdevices

    client = discord.Client()

    # Keywords to trigger the bot
    welcome_phrases = ['hello', 'hey', 'hi', 'howdy', 'yo', 'sup']
    goodbye_phrases = ['cya', 'bye', 'ciao', 'goodnight']
    nice_words = ['love', 'like', 'best', 'nice', 'happy', 'hug']
    naughty_words = ['hate', 'fuck', 'screw', 'shit', 'crap', 'bastard', 'cunt', 'pussy', 'dick', 'ass',
                     'dumb', 'stupid', 'bitch', 'hate', 'dislike', 'suck']

    def turn_on_everything():

        media_room_camera = pyHS100.SmartPlug(get_smartdevices.address(category='smartplugs', name='media_room_camera'))
        back_room_camera = pyHS100.SmartPlug(get_smartdevices.address(category='smartplugs', name='back_room_camera'))

        # Turn on Lights
        try:
            lights = get_smartdevices.address(category='lifx', zone='media_room')
            c = lifx.Connection(lights)
            c.power_on()

        except Exception as e:
            print(e)

        # Turn on Lights
        try:
            w = wifi370.Connection()
            w.color(color[0], color[1], color[2], color[3])

        except Exception as e:
            print(e)

        # Turn Off Camera
        try:
            media_room_camera.turn_off()
            back_room_camera.turn_off()

        except Exception as e:
            print(e)

        # Turn on PC
        try:
            send_magic_packet('04.D9.F5.7C.0D.B3', '68.05.CA.9F.00.49')  # Turn on PC

        except Exception as e:
            print(e)

        # Turn on Receiver
        try:
            rec = receiver.Main()
            rec.power_on()

        except Exception as e:
            print(e)

    @client.event
    async def on_ready():
        print("Bot Connected.")
        channel = client.get_channel(channel_id)

        response = "@everyone I'm Alive!"
        await channel.send(response)

    @client.event
    async def on_message(message):

        if message.author is not client.user:

            # Get Smart Devices
            sub = pyHS100.SmartPlug(get_smartdevices.address(category='smartplugs', name='subwoofer'))
            media_room_camera = pyHS100.SmartPlug(get_smartdevices.address(category='smartplugs', name='media_room_camera'))
            back_room_camera = pyHS100.SmartPlug(get_smartdevices.address(category='smartplugs', name='back_room_camera'))
            rec = receiver.Main()

            print('user: %s msg: %s' % (message.author, message.content))

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
            elif bot_name.lower() in message_content or str(bot_id) in message_content:

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
                        response = ":heart_eyes: "

            # Respond to a what is query!
            elif "what is" in message_content:

                if "weather" in message_content:
                    response = "I dunno, depends where you live I guess..."

            # //////////////////////////////////////////////////////////////////
            # Smart Home Stuff!
            else:
                if any(user in str(message.author) for user in trusted_users):

                    # Turn on everything!
                    if "turn on everything" in message_content:

                        turn_on_everything()
                        response = "You got it!"

                    elif "home" in message_content:

                        turn_on_everything()
                        response = "Welcome home!"

                    elif "awake" in message_content:

                        turn_on_everything()
                        response = "I turned on everything for you!"

                    elif ("other pc" in message_content) and ("on" in message_content):

                        send_magic_packet('F8.32.E4.6D.D4.B4')  # Turn on PC
                        response = "Okay."

                    elif "anime" in message_content:

                        sub.turn_on()
                        rec.set_input('tv')
                        time.sleep(1)
                        rec.set_volume('121')
                        lifx_presets.main('movie')

                        response = "Enjoy your anime!"

                    elif "sub" in message_content:

                        if "on" in message_content:
                            response = "Enjoy the bass!"
                            sub.turn_on()

                        if "off" in message_content:
                            response = "No bass for you then!."
                            sub.turn_off()

                    elif "camera" in message_content:

                        if "on" in message_content:
                            response = "Security systems activated!"
                            media_room_camera.turn_on()
                            back_room_camera.turn_on()

                        if "off" in message_content:
                            response = "You may now do your dirty deeds..."
                            media_room_camera.turn_off()
                            back_room_camera.turn_off()

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

                        elif ("bedroom" in message_content) or ("bed room" in message_content):
                            response = "Okay, I'll set the speakers to the Bedroom."
                            rec.power_on()

                            time.sleep(2)  # Prevent Socket Spam
                            rec.set_input('bedroom')

                        elif ("mediaroom" in message_content) or ("media room" in message_content):
                            response = "Okay, I'll set the speakers to the Media Room."
                            rec.power_on()

                            time.sleep(2)  # Prevent Socket Spam
                            rec.set_input('pc')

                    # Lights On/Off
                    elif "light" in message_content:

                        if "bed" in message_content:

                            lights = get_smartdevices.address(category='lifx', zone='bedroom')
                            c = lifx.Connection(lights)

                            if "on" in message_content:
                                c.power_on()
                                response = "Enjoy your reading..."

                            if "off" in message_content:
                                c.power_off()
                                response = "Goodnight..."

                        else:
                            lights = get_smartdevices.address(category='lifx', zone='media_room')
                            c = lifx.Connection(lights)
                            w = wifi370.Connection()

                            if "on" in message_content:
                                response = "Let there be light!"
                                c.power_on()
                                w.color(color[0], color[1], color[2], color[3])

                            elif "off" in message_content:
                                response = "Enjoy the darkness...."
                                c.power_off()
                                w.turn_off()

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
                print('Replying with: %s\n' % response)

            # ----------------------------------------------------------
            # ----------------------------------------------------------

        else:
            return

    # Run
    client.run(token)


# Thread for Checking new Episodes!
def check_episodes_thread():
    cmd = [python_bin, '-c', 'import sys\nsys.path.append(\'' + script_path + '\')\n' +
           'import discord_bot, importlib\nimportlib.reload(discord_bot)\ndiscord_bot.check_new_episodes()']

    proc = subprocess.Popen(cmd).communicate()
    _stdout, _stderr = proc

    if _stdout:
        print(_stdout)
    if _stderr:
        print(_stderr)


def discord_bot_thread():
    cmd = [python_bin, '-c', 'import sys\nsys.path.append(\'' + script_path + '\')\n' +
           'import discord_bot, importlib\nimportlib.reload(discord_bot)\ndiscord_bot.discord_bot()']

    proc = subprocess.Popen(cmd).communicate()
    _stdout, _stderr = proc

    if _stdout:
        print(_stdout)
    if _stderr:
        print(_stderr)


# Run
if __name__ == "__main__":

    print("Running Discord Bot")

    # Run Threads
    t1 = threading.Thread(target=discord_bot_thread, daemon=True)
    t2 = threading.Thread(target=check_new_episodes, daemon=True)
    t1.start()
    t2.run()
