# Static Sensors

import os
import sys
import time
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


def get_receiver_state():

    import receiver
    import json
    import datetime

    export_path = '/mnt/tmp/sensor_data/sensors'
    path = os.path.join(export_path, 'receiver.json')

    now = datetime.datetime.now()
    time_now = now.strftime("%Y-%m-%d %H:%M:%S")

    output = {'sensor_name': 'receiver', 'time': time_now, 'power': 0, 'raw_vol': 0, 'vol': 0, "input": 0}

    try:
        rec = receiver.Main()
        current_power = rec.get_power()

        if "PWR0" in current_power:
            power_state = 1

        else:
            power_state = 0

        time.sleep(1)
        current_volume = rec.get_volume()

        time.sleep(1)
        current_input = rec.get_input()[1]

        output['power'] = power_state
        output['raw_vol'] = current_volume[0]
        output['vol'] = current_volume[1]
        output['input'] = current_input

    except Exception as e:
        print(e)
        pass

    # Write to File
    json_output = json.dumps(output)
    with open(path, 'w+') as outfile:
        outfile.write(json_output)

    return output


def main():

    ip_sensor_data = ip_sensor.main()
    vpn_nyaa = None
    vpn_iptorrents = None
    receiver_stats = get_receiver_state()

    # Get Smart Devices
    # subwoofer = get_smartplug_state('subwoofer')
    study_camera = get_smartplug_state('study_camera')
    living_room_camera = get_smartplug_state('living_room_camera')

    # IP / VPN Sensors
    for row in ip_sensor_data:
        if row['machine'] == 'ds918-transmission':
            vpn_nyaa = row['vpn_connected']

        if row['machine'] == 'ubuntu-transmission':
            vpn_iptorrents = row['vpn_connected']

    data = {
        # 'subwoofer': subwoofer,
        'study_camera': study_camera,
        'living_room_camera': living_room_camera,
        'vpn_nyaa': vpn_nyaa,
        'vpn_iptorrents': vpn_iptorrents,
        'receiver_power': receiver_stats['power'],
        'receiver_vol': receiver_stats['vol'],
        'receiver_input': receiver_stats['input']
    }

    return data


if __name__ == "__main__":
    a = main()
    print(a)
