import os
import json
import datetime

path_to_sensors = '/mnt/tmp/ip_addr'


def load_data():

    output = []

    for sensor in os.listdir(path_to_sensors):
        sensor_path = os.path.join(path_to_sensors, sensor)

        with open(sensor_path, 'r') as sensor_data:

            data = sensor_data.read()
            data = json.loads(data)
            output.append({'machine': sensor.split('.')[0], 'data': data})

    return output


def main():

    """

    Status Codes

    0 = Disconnected
    1 = Connected
    2 = Unknown

    """

    data = load_data()

    new_data = []
    for machine in data:

        # DEBUG
        # print(machine)

        # Check if data is recent! (last 5 minutes)
        now = datetime.datetime.now()
        recorded_time = datetime.datetime.strptime(machine['data']['time'], '%Y-%m-%d %H:%M:%S.%f')

        difference = now - recorded_time

        if difference.seconds < 180:
            active = 1

        else:
            active = 0

        # Check if matches VPN Country
        if active == 1:
            if machine['data']['country'] == 'Singapore':
                connected = 1

            else:
                connected = 0

        # Unknown Status
        elif active == 0:
            connected = 2

        # Append new data
        new_data.append({'machine': machine['machine'], 'vpn_connected': connected})

    return new_data


if __name__ == "__main__":
    a = main()
    print(a)
