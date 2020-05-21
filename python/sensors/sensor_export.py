# http://oz123.github.io/writings/2019-06-16-Visualize-almost-anything-with-Grafana-and-Python/index.html
# https://blog.jonathanmccall.com/2018/10/09/creating-a-grafana-datasource-using-flask-and-the-simplejson-plugin/
# http://www.oznetnerd.com/writing-a-grafana-backend-using-the-simple-json-datasource-flask/

from bottle import (Bottle, HTTPResponse, run, request, response,
                    json_dumps as dumps)
import switch_bot_sensor
import pi_temp
import hs110_power_monitor
import weatherzone
import internet_ping
import static_sensors
import logging
import threading
import time
import os
import json
from calendar import timegm
from datetime import datetime, timedelta
import atexit

dir_path = '/mnt/tmp/sensor_data'
json_export_path = os.path.join(dir_path, 'sensors')
logging_path = os.path.join('/mnt/tmp/logs', 'sensor_export.log')
logging.basicConfig(level=logging.INFO)
logging.basicConfig(filename=logging_path, filemode='w', format='%(asctime)s %(message)s', datefmt='%d/%m/%Y %I:%M:%S')
time_delay = 30

# Get Ping on Reset
ping = internet_ping.get_ping()
net_alive = internet_ping.get_alive()

data = {}
static_data = {}

# List of Sensors

sensor_list = [
    'media_room_temperature', 'media_room_humidity',
    'bed_room_temperature', 'bed_room_humidity', 'Pi_Cpu_temp',
    'hs110_volts', 'hs110_watts', 'outside_temp', 'ping', 'net_alive'
]

# Get Static Sensors
static_sensor_list = []
for x in static_sensors.main():
    static_sensor_list.append(x)


def get_current_time():
    return int(datetime.now().strftime("%s"))


def convert_to_time_ms(timestamp):
    return 1000 * timegm(
            datetime.strptime(
                timestamp, '%Y-%m-%dT%H:%M:%S.%fZ').timetuple())


def get_data():

    logging.debug("Getting Info")
    input_data = {}

    for sensor in sensor_list:

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
    global static_data

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

        print('Static Sensors %s' % static_sensor_list)

        return HTTPResponse(body=dumps(sensor_list + static_sensor_list), headers={'Content-Type': 'application/json'})

    @app.post('/query')
    def query():

        start, end = request.json['range']['from'], request.json['range']['to']

        new_data = None

        for target in request.json['targets']:
            name = target['target']

            for sensor in sensor_list:

                if name == sensor:
                    new_data = convert_to_datapoints(data, name, start, end)

            if new_data is None:

                for sensor in static_sensor_list:

                    if name == sensor:
                        new_data = convert_to_datapoints(static_data, name, start, end)

        body = dumps(new_data)
        return HTTPResponse(body=body, headers={'Content-Type': 'application/json'})

    if __name__ == '__main__':
        run(app=app, host='0.0.0.0', port=8081)


# Convert Incoming Query to Datapoints for Grafana
def convert_to_datapoints(input_data, name, start, end):

    lower = convert_to_time_ms(start)
    upper = convert_to_time_ms(end)

    new_data = [{"target": name, "datapoints": []}]

    for item in input_data:

        # Check if name matches
        if name == item:

            # Check if within range
            for point in input_data[item]:
                new_point = point[0], point[1] * 1000
                if lower < new_point[1] < upper:
                    new_data[0]["datapoints"].append(new_point)

    return new_data


# A place to store additional sensor ops on a thread
def additional_sensors_thread():

    global ping
    global net_alive

    while True:
        ping = internet_ping.get_ping()
        net_alive = internet_ping.get_alive()

        time.sleep(15)


def static_sensor_thread():

    global static_data

    while True:

        # Get Static Sensor Data
        static_sensor_data = static_sensors.main()

        now = get_current_time()
        new_data = {}

        for sensor in static_sensor_data:
            new_data.update({sensor: [[static_sensor_data[sensor], now]]})

        static_data = new_data

        # Standard Delay
        time.sleep(5)


def sensor_export_thread():

    global data
    global ping
    global net_alive
    logging.info("Initializing Sensor Export Thread")

    # Infinite Loop
    while True:

        now = get_current_time()
        switchbot_sensor_data = []
        sensors = os.listdir(json_export_path)

        # Read Previous Sensor Data from Disk
        for sensor in sensors:
            try:
                with open(os.path.join(json_export_path, sensor)) as json_file:
                    switchbot_sensor_data.append(json.load(json_file))

            except Exception as e:
                logging.error(e)
                print('Cannot Load: %s' % sensor)
                pass

        try:
            # Get Current Sensor Data
            switch_bot_sensor.main(json_export_path)
            pi_current_temp = float(pi_temp.measure_temp())

            hs110_monitor = hs110_power_monitor.sensor_export()
            outside_temp = weatherzone.get_temp()
            new_data = get_data()

            # Update with latest Switch bot Sensor Readings
            for sensor in switchbot_sensor_data:

                if sensor['sensor_name'] == 'bed_room':
                    new_data['bed_room_temperature'].append([sensor['temperature'], now])
                    new_data['bed_room_humidity'].append([sensor['humidity'], now])
                    # new_data['bed_room_battery'].append([sensor['battery'], now])

                if sensor['sensor_name'] == 'media_room':
                    new_data['media_room_temperature'].append([sensor['temperature'], now])
                    new_data['media_room_humidity'].append([sensor['humidity'], now])
                    # new_data['media_room_battery'].append([sensor['battery'], now])

            # Other Sensors
            new_data['Pi_Cpu_temp'].append([pi_current_temp, now])
            new_data['hs110_volts'].append([hs110_monitor[0], now])
            new_data['hs110_watts'].append([hs110_monitor[1], now])
            new_data['outside_temp'].append([outside_temp, now])
            new_data['ping'].append([ping, now])
            new_data['net_alive'].append([net_alive, now])

            # Write Data to Disk
            write_data(new_data)
            stored_data = new_data

            # Update Data in Memory
            data = stored_data
            print('Finished Writing Data!')

        except Exception as e:
            logging.exception(e)

        # Sleep for Time Delay
        time.sleep(time_delay)


def save_on_exit():

    global data
    logging.info('saving data to disk before closing...')
    write_data(data)


def write_data(new_data):

    now = datetime.now()

    for sensor in sensor_list:
        sensor_path = os.path.join(dir_path, sensor + '.json')
        sensor_data = new_data[sensor]

        pruned_data = []

        for sample in sensor_data:
            timestamp = datetime.fromtimestamp(sample[1])

            if timestamp > (now - timedelta(days=7)):
                pruned_data.append(sample)

        # Add Pruned Data to Export
        export_data = {sensor: pruned_data}

        print('writing to: %s' % sensor_path)
        with open(sensor_path, 'w+') as json_file:
            json.dump(export_data, json_file, indent=2)


# Register Exit Handler
atexit.register(save_on_exit)

# Initialize and Start Threads
t1 = threading.Thread(target=bottle_thread)
t2 = threading.Thread(target=sensor_export_thread)
t3 = threading.Thread(target=static_sensor_thread)
t4 = threading.Thread(target=additional_sensors_thread)

t1.start()
t2.start()
t3.start()
t4.start()
