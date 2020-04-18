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
from bottle import Bottle, run

# Get Smart Devices
media_room_camera = pyHS100.SmartPlug(get_smartdevices.address(category='smartplugs', name='media_room_camera'))
back_room_camera = pyHS100.SmartPlug(get_smartdevices.address(category='smartplugs', name='back_room_camera'))
subwoofer = pyHS100.SmartPlug(get_smartdevices.address(category='smartplugs', name='subwoofer'))

receiver_data = {}
smart_device_data = {}
computer_data = {}

# Get Logger
logger = luma_log.main(__file__)


def web_server():

    app = Bottle()

    @app.route("/", method=['GET', 'OPTIONS'])
    def index():

        content = '<p>receiver_data: %s</p>' % str(receiver_data)
        content += '<p>smart_device_data: %s</p>' % str(smart_device_data)
        return content

    run(app=app, host='0.0.0.0', port=8081)


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
            current_volume = str(data['vol']) + ' dB'
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
