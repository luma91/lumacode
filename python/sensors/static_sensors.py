# Static Sensors

import os
import sys
import pyHS100
import ip_sensor

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))


def remap_state(state):

    status = 0
    if state == "ON":
        status = 1

    return status


def get_smartplug_state(name):

    import get_smartdevices

    try:
        device = pyHS100.SmartPlug(get_smartdevices.address(category='smartplugs', name=name))
        state = remap_state(device.state)

    except Exception as e:
        state = 0
        print('Error on %s: %s' % (name, e))

    return state


def main():

    ip_sensor_data = ip_sensor.main()
    vpn_nyaa = None
    vpn_iptorrents = None

    # Get Smart Devices
    subwoofer = get_smartplug_state('subwoofer')
    media_room_camera = get_smartplug_state('media_room_camera')
    back_room_camera = get_smartplug_state('back_room_camera')
    receiver_power = 0
    receiver_vol = 0
    receiver_input = 0

    # IP / VPN Sensors
    for row in ip_sensor_data:
        if row['machine'] == 'ds918-transmission':
            vpn_nyaa = row['vpn_connected']

        if row['machine'] == 'ubuntu-transmission':
            vpn_iptorrents = row['vpn_connected']

    data = {
        'subwoofer': subwoofer,
        'media_room_camera': media_room_camera,
        'back_room_camera': back_room_camera,
        'vpn_nyaa': vpn_nyaa,
        'vpn_iptorrents': vpn_iptorrents,
        'receiver_power': receiver_power,
        'receiver_vol': receiver_vol,
        'receiver_input': receiver_input
    }

    return data


if __name__ == "__main__":
    a = main()
    print(a)
