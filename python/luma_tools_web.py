# References
# https://stackoverflow.com/questions/27090263/how-to-use-ajax-for-auto-refresh-a-div-or-a-web-page

import wifi370
import lifx
import lifx_presets
import luma_log
import receiver
import get_smartdevices
import pyHS100

import json
import time
import threading
from flask import Flask, request
from werkzeug.exceptions import BadRequest

# Get Smart Devices
media_room_camera = pyHS100.SmartPlug(get_smartdevices.address(category='smartplugs', name='media_room_camera'))
back_room_camera = pyHS100.SmartPlug(get_smartdevices.address(category='smartplugs', name='back_room_camera'))
subwoofer = pyHS100.SmartPlug(get_smartdevices.address(category='smartplugs', name='subwoofer'))

receiver_data = {}
smart_device_data = {}
computer_data = {}

# Get Logger
logger = luma_log.main(__file__)

# Get Inputs
receiver_inputs = get_smartdevices.get_receiver_inputs()


def web_server():

    app = Flask(__name__)

    @app.route("/", methods=["GET", "POST"])
    def index():

        path_to_css = 'static/css/luma_tools_web.css?' + str(time.time()).split('.')[0]
        header = open('static/templates/header.html').read()
        header = header.replace('$CSS_PATH', path_to_css)

        # Page Body
        body = '<div class="container">\n'
        body += '<div class="header"><span class="highlight">Luma Tools: </span>Web</div>\n'

        body += '<div class="content">\n'

        body += '<div class="status_grp">'
        body += '<span class="item">Receiver Power: <span style="font-weight: bold;" id="rec_power">%s</span></span>\n' % str(receiver_data['power'])
        body += '<span class="item">Current Input: <span style="font-weight: bold;" id="rec_input">%s</span></span>\n' % str(receiver_data['current_input']).upper()
        body += '</div>'

        # Lifx
        body += '<div class="lifx_grp">\n'
        body += '<span class="label_text">LIFX Power:</span>'
        body += '<button class="button" type="button" onclick="send_command(\'lifx\', \'power\', \'on\')">Power On</button>'
        body += '<button class="button" type="button" onclick="send_command(\'lifx\', \'power\', \'off\')">Power Off</button>'
        body += '</div>'

        # Receiver Power
        body += '<div class="receiver_grp">'
        body += '<span class="label_text">Receiver Power:</span>'
        body += '<button class="button" type="button" onclick="send_command(\'receiver\', \'power\', \'on\')">Power On</button>'
        body += '<button class="button" type="button" onclick="send_command(\'receiver\', \'power\', \'off\')">Power Off</button>'
        body += '<button class="button" type="button" onclick="send_command(\'receiver\', \'mute\', \'toggle\')">Toggle Mute</button>'

        # Receiver Volume
        body += '<div class="rec_vol">'
        body += '<span class="label_text">Receiver Volume:</span>'
        body += '<input type="range" onchange="update_vol()" id="vol" name="vol" min="45" max="120" ' \
                'value="' + str(receiver_data['raw_volume']) + '">'
        body += '<span id="current_vol">' + str(receiver_data['current_volume']) + 'db</span>'
        body += '</div>'

        # body += '<button class="button" type="button" onclick="var vol=document.getElementById(\'vol\').value; ' \
        #         ' send_command(\'receiver\', \'volume\', vol)">Change Volume</button>'

        # Receiver Input
        body += '<form id="rec_input">\n'
        body += '<span class="label_text">Receiver Input:</span> <select name="receiver_input" type="text">\n'

        # Add Receiver Inputs
        for rec_input in receiver_inputs:
            if receiver_data['current_input'] == rec_input:
                body += '<option value="' + rec_input + '" selected="selected">' + rec_input + '</option>'
            else:
                body += '<option value="' + rec_input + '">' + rec_input + '</option>'

        body += '</select>\n'

        body += '<input class="button" id="submit" type="submit" value="Change Input"></input>\n'
        body += '</form>\n'

        body += '</div>\n'
        body += '</div>\n'

        body += '</div>\n'

        # Add Footer and Compile the Page
        footer = open('static/templates/footer.html').read()
        content = header + body + footer

        return content

    @app.route("/ops", methods=["POST"])
    def ops():

        if request.method == "POST":

            # Receiver
            receiver_input = request.form.get('receiver_input')
            data = request.get_json()

            if receiver_input:

                try:
                    rec = receiver.Main()
                    if receiver_input != receiver_data['current_input']:
                        rec.set_input(value=receiver_input)

                except Exception as e:
                    return 'Error: %s' % e

            if data:
                if data['device'] == 'receiver':

                    command = data['command']

                    try:
                        rec = receiver.Main()

                        if data['operation'] == 'power':

                            if command == 'on':
                                rec.power_on()

                            elif command == 'off':
                                rec.power_off()

                        if data['operation'] == 'mute':
                            rec.mute()

                        if data['operation'] == 'volume':
                            rec.set_volume(command.zfill(3))

                    except Exception as e:
                        return 'Error: %s' % e, 500

        # Go Back Home
        return 'OK', 200

    @app.route("/query", methods=["POST"])
    def query():

        result = None
        if request.method == "POST":
            data = request.get_json()

            if data['device'] == 'receiver':
                if data['item'] == 'current_vol':
                    result = str(receiver_data['current_volume'])

                if data['item'] == 'convert_vol':
                    result = str(receiver.remap_to_db(data['value']))

        return result

    # Run the Server
    app.run(host='0.0.0.0', port=8080)

    # -------------------------


def check_receiver():

    global receiver_data
    receiver_path = '/mnt/tmp/sensor_data/sensors/receiver.json'

    while True:

        try:
            with open(receiver_path) as json_file:
                data = (json.load(json_file))

            current_power = int(data['power'])

            power = "OFF"
            if current_power == 1:
                power = "ON"

            raw_volume = int(data['raw_vol'])
            current_volume = str(data['vol'])
            current_input = data['input']

            receiver_data = {
                'power': power,
                'raw_volume': raw_volume,
                'current_volume': current_volume,
                'current_input': current_input
            }

        except Exception as e:

            logger.error(e)
            print("Error checking receiver. Will try again shortly.")

        time.sleep(3)


def check_smart_devices():

    global smart_device_data

    while True:

        try:

            lifx_conn_mr = lifx.Connection(get_smartdevices.address(category='lifx', zone='media_room'))
            lifx_power_mr = 'OFF'

            if lifx_conn_mr.power_status() != 0:
                lifx_power_mr = 'ON'

            # Get Smart Device State
            smart_device_data = {
                'subwoofer': subwoofer.state,
                'media_room_lifx': lifx_power_mr,
                'media_room_camera': media_room_camera.state,
                'back_room_camera': back_room_camera.state
            }

        except Exception as e:

            logger.error(e)
            print("Error checking smart devices. Will try again shortly.")

        time.sleep(3)


def check_computers():
    pass


if __name__ == "__main__":

    # Start the Checking Threads
    t1 = threading.Thread(target=check_receiver)
    t2 = threading.Thread(target=check_smart_devices)
    t3 = threading.Thread(target=check_computers)

    t1.start()
    t2.start()
    t3.start()

    # Run the Web Server
    web_server()
