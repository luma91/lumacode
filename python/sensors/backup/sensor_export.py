# http://oz123.github.io/writings/2019-06-16-Visualize-almost-anything-with-Grafana-and-Python/index.html
# https://blog.jonathanmccall.com/2018/10/09/creating-a-grafana-datasource-using-flask-and-the-simplejson-plugin/
# http://www.oznetnerd.com/writing-a-grafana-backend-using-the-simple-json-datasource-flask/

from bottle import (Bottle, HTTPResponse, run, request, response,
                    json_dumps as dumps)
import switch_bot_sensor
import pi_temp
import hs110_power_monitor
import weatherzone
import ip_sensor
import logging
import threading
import time
import os
import json
from calendar import timegm
from datetime import datetime, timedelta

dir_path = '/mnt/tmp/sensor_data'
json_export_path = os.path.join(dir_path, 'sensors')
logging.basicConfig(level=logging.INFO)
time_delay = 30
data = {}

# List of Sensors
sensor_list = ['media_room_temperature', 'media_room_humidity', 'media_room_battery',
               'bed_room_temperature', 'bed_room_humidity', 'bed_room_battery', 'Pi_Cpu_temp',
               'hs110_volts', 'hs110_watts', 'outside_temp', 'vpn_nyaa', 'vpn_iptorrents']


def get_current_time():
    return int(datetime.now().strftime("%s")) * 1000 


def convert_to_time_ms(timestamp):
    return 1000 * timegm(
            datetime.strptime(
                timestamp, '%Y-%m-%dT%H:%M:%S.%fZ').timetuple())


def get_data():

    logging.debug("Getting Info")
    input_data = {}

    for sensor in sensor_list:

        '''
        # Only Load Target Sensor Data
        if target_name:
            if sensor.lower() in target_name.lower():
                sensor_path = os.path.join(dir_path, sensor + '.json')

                with open(sensor_path) as json_file:
                    input_data.update(json.load(json_file))
        '''

        # Load All Sensor Data
        sensor_path = os.path.join(dir_path, sensor + '.json')

        try:
            with open(sensor_path) as json_file:
                input_data.update(json.load(json_file))

        except OSError or FileNotFoundError:
            print('Cannot Load: %s' % sensor_path)

            # Create empty data
            input_data.update({sensor: []})

    return input_data


def bottle_thread():

    global data
    logging.info("Initializing Bottle Thread")
    app = Bottle()

    @app.hook('after_request')
    def enable_cors():
        logging.debug("after_request hook")
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Accept, Content-Type'

    @app.route("/", method=['GET', 'OPTIONS'])
    def index():
        return 'OK'
        
    @app.post('/search')
    def search():
        return HTTPResponse(body=dumps(sensor_list), headers={'Content-Type': 'application/json'})

    @app.post('/query')
    def query():

        start, end = request.json['range']['from'], request.json['range']['to']

        new_data = None
        for target in request.json['targets']:
            name = target['target']
            # data = get_data(name)
            new_data = convert_to_datapoints(data, name, start, end)
        
        body = dumps(new_data)
        return HTTPResponse(body=body, headers={'Content-Type': 'application/json'})

    if __name__ == '__main__':
        run(app=app, host='0.0.0.0', port=8081)


# Convert Incoming Query to Datapoints for Grafana
def convert_to_datapoints(data, name, start, end):

    lower = convert_to_time_ms(start)
    upper = convert_to_time_ms(end)

    new_data = [{"target": name, "datapoints": []}]

    for x in data:

        # Check if name matches
        if name == x:

            # Check if within range
            for point in data[x]:
                if lower < point[1] < upper:
                    new_data[0]["datapoints"].append(point)

    return new_data


def sensor_export_thread():

    global data
    logging.info("Initializing Sensor Export Thread")

    # Infinite Loop
    while True:

        switchbot_sensor_data = []
        sensors = os.listdir(json_export_path)

        # Read Previous Sensor Data from Disk
        for sensor in sensors:
            try:
                with open(os.path.join(json_export_path, sensor)) as json_file:
                    switchbot_sensor_data.append(json.load(json_file))

            except OSError or FileNotFoundError:
                print('Cannot Load: %s' % sensor)
                pass

        # Get Current Sensor Data
        switch_bot_sensor.main(json_export_path)
        now = get_current_time()
        pi_current_temp = float(pi_temp.measure_temp())
        hs110_monitor = hs110_power_monitor.sensor_export()
        outside_temp = weatherzone.get_temp()
        ip_sensor_data = ip_sensor.main()

        logging.debug("Existing file. Updating latest measurements.")
        new_data = get_data()

        # Update with latest Switch bot Sensor Readings
        for sensor in switchbot_sensor_data:

            if sensor['sensor_name'] == 'bed_room':
                new_data['bed_room_temperature'].append([sensor['temperature'], now])
                new_data['bed_room_humidity'].append([sensor['humidity'], now])
                new_data['bed_room_battery'].append([sensor['battery'], now])

            if sensor['sensor_name'] == 'media_room':
                new_data['media_room_temperature'].append([sensor['temperature'], now])
                new_data['media_room_humidity'].append([sensor['humidity'], now])
                new_data['media_room_battery'].append([sensor['battery'], now])

        # IP / VPN Sensors
        for row in ip_sensor_data:
            if row['machine'] == 'ds918-transmission':
                vpn_nyaa = row['vpn_connected']
                new_data['vpn_nyaa'].append([vpn_nyaa, now])

            if row['machine'] == 'ubuntu-transmission':
                vpn_iptorrents = row['vpn_connected']
                new_data['vpn_iptorrents'].append([vpn_iptorrents, now])

        # Other Sensors
        new_data['Pi_Cpu_temp'].append([pi_current_temp, now])
        new_data['hs110_volts'].append([hs110_monitor[0], now])
        new_data['hs110_watts'].append([hs110_monitor[1], now])
        new_data['outside_temp'].append([outside_temp, now])

        for row in new_data:
            sensor_path = os.path.join(dir_path, row + '.json')
            export_data = {row: new_data[row]}

            print('writing to: %s' % sensor_path)
            with open(sensor_path, 'w+') as json_file:
                json.dump(export_data, json_file, indent=2)

        # Update Data in Memory
        data = new_data

        # Sleep for Time Delay
        time.sleep(time_delay)


t1 = threading.Thread(target=bottle_thread)
t1.start()

t2 = threading.Thread(target=sensor_export_thread)
t2 = threading.Thread(target=sensor_export_thread)
t2.start()
