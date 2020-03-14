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

    data = load_data()

    new_data = []
    for machine in data:

        # DEBUG
        print(machine)

        # Check if data is recent! (last 5 minutes)
        now = datetime.datetime.now()
        time = datetime.datetime.strptime(machine['data']['time'], '%Y-%m-%d %H:%M:%S.%f')

        difference = now - time
        if difference.seconds < 70:
            active = 1

        else:
            active = 0

        # Check if matches VPN Country
        if machine['data']['country'] == 'Singapore' and active == 1:
            connected = 1

        else:
            connected = 0

        # Append new data
        new_data.append({'machine': machine['machine'], 'vpn_connected': connected})

    return new_data


if __name__ == "__main__":
    main()
