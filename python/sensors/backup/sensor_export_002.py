# http://oz123.github.io/writings/2019-06-16-Visualize-almost-anything-with-Grafana-and-Python/index.html
# https://blog.jonathanmccall.com/2018/10/09/creating-a-grafana-datasource-using-flask-and-the-simplejson-plugin/
# http://www.oznetnerd.com/writing-a-grafana-backend-using-the-simple-json-datasource-flask/

from bottle import (Bottle, HTTPResponse, run, request, response,
                    json_dumps as dumps)
import switch_bot_sensor
import pi_temp
import hs110_power_monitor
import logging
import threading
import time
import os
import pprint
import json
from calendar import timegm
from datetime import datetime, timedelta

dir_path = os.path.dirname(os.path.realpath(__file__))
json_export_path = os.path.join(dir_path, 'data', 'sensors')
json_export_timehistory = os.path.join(dir_path, 'data')  # 'sensor_data_history.json'
logging.basicConfig(level=logging.INFO)
time_delay = 30

# List of Sensors
sensor_list = ['media_room_temperature', 'media_room_humidity', 'media_room_battery',
               'bed_room_temperature', 'bed_room_humidity', 'bed_room_battery', 'Pi_Cpu_temp',
               'hs110_volts', 'hs110_watts']


def get_current_time():
    return int(datetime.now().strftime("%s")) * 1000 


def convert_to_time_ms(timestamp):
    return 1000 * timegm(
            datetime.strptime(
                timestamp, '%Y-%m-%dT%H:%M:%S.%fZ').timetuple())


def get_data(target_name=None):

    logging.debug("Getting Info")
    input_data = []

    for sensor in sensor_list:
        
        # Only Load Target Sensor Data
        if target_name:
            if sensor.lower() in target_name.lower():
                sensor_path = os.path.join(json_export_timehistory, sensor + '.json')

                with open(sensor_path) as json_file:
                    input_data.append(json.load(json_file))
                    
                print(target_name)
        
        # Load All Sensor Data
        else:
            sensor_path = os.path.join(json_export_timehistory, sensor + '.json')

            with open(sensor_path) as json_file:
                input_data.append(json.load(json_file))

    return input_data


def bottle_thread():
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

        for target in request.json['targets']:
            name = target['target']
            data = get_data(name)
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
        if name.lower() == x['target'].lower():

            # Check if within range
            for point in x['datapoints']:
                if point[1] > lower and point[1] < upper:
                    new_data[0]["datapoints"].append(point)

    return new_data


def sensor_export_thread():

    logging.info("Initializing Sensor Export Thread")

    # Infinite Loop
    while True:

        # Get Switch-bot Sensor Data
        switch_bot_sensor.main(json_export_path)
        sensors = os.listdir(json_export_path)
        input_data = []

        for sensor in sensors:

            with open(os.path.join(json_export_path, sensor)) as json_file:
                input_data.append(json.load(json_file))

        now = get_current_time()
        pi_current_temp = float(pi_temp.measure_temp())
        hs110_monitor = hs110_power_monitor.sensor_export()

        # Time Series
        formatted_data = [
            {"target": "media_room_Temperature", "datapoints": [[input_data[0]['temperature'], now]]},
            {"target": "media_room_Humidity", "datapoints": [[input_data[0]['humidity'], now]]},
            {"target": "media_room_Battery", "datapoints": [[input_data[0]['battery'], now]]},
            {"target": "bed_room_Temperature", "datapoints": [[input_data[1]['temperature'], now]]},
            {"target": "bed_room_Humidity", "datapoints": [[input_data[1]['humidity'], now]]},
            {"target": "bed_room_Battery", "datapoints": [[input_data[1]['battery'], now]]},
            {"target": "Pi_Cpu_temp", "datapoints": [[pi_current_temp, now]]},
            {"target": "hs110_volts", "datapoints": [[hs110_monitor[0], now]]},
            {"target": "hs110_watts", "datapoints": [[hs110_monitor[1], now]]}
        ]

        # History exists, append
        try:
            logging.debug("Existing file. Updating latest measurements.")
            data = get_data()

            new_data = data
            new_data[0]["datapoints"].append([input_data[0]['temperature'], now])
            new_data[1]["datapoints"].append([input_data[0]['humidity'], now])
            new_data[2]["datapoints"].append([input_data[0]['battery'], now])
            new_data[3]["datapoints"].append([input_data[1]['temperature'], now])
            new_data[4]["datapoints"].append([input_data[1]['humidity'], now])
            new_data[5]["datapoints"].append([input_data[1]['battery'], now])
            new_data[6]["datapoints"].append([pi_current_temp, now])
            new_data[7]["datapoints"].append([hs110_monitor[0], now])
            new_data[8]["datapoints"].append([hs110_monitor[1], now])

            num = 0

            for sensor in sensor_list:
                sensor_path = os.path.join(json_export_timehistory, sensor + '.json')
                with open(sensor_path, 'w+') as json_file:
                    json.dump(new_data[num], json_file, indent=2)
                num += 1

        # History doesnt exist, or JSON error, create a new one.
        except Exception as e:

            logging.error(e)
            num = 0
            for sensor in sensor_list:
                try:
                    sensor_path = os.path.join(json_export_timehistory, sensor + '.json')

                    with open(sensor_path, 'w+') as json_file:
                        json.dump(formatted_data[num], json_file, indent=2)
                    num += 1

                except IndexError:
                    logging.error('Sensor data missing.')

        # Sleep for Time Delay
        time.sleep(time_delay)


t1 = threading.Thread(target=bottle_thread)
t1.start()

t2 = threading.Thread(target=sensor_export_thread)
t2 = threading.Thread(target=sensor_export_thread)
t2.start()
