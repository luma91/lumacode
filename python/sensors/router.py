# dbhost='192.168.0.45:8085'
# curl -i -XPOST "http://$dbhost/" --data-binary $payload


import subprocess
from datetime import datetime, timedelta
import json
from bottle import (Bottle, HTTPResponse, run, request, response, json_dumps as dumps)


def get_current_time():
    return int(datetime.now().strftime("%s")) * 1000


def convert_payload(data):

    sensor = data[0]['name']
    columns = data[0]['columns']
    points = data[0]['points']

    num = 0
    processed_data = {}

    for column in columns:
        processed_data[column] = str(points[num])
        num += 1

    # Single Entries
    if any(x for x in ['router_assoclist'] if x in sensor):
        return sensor + ' ' + columns[0] + '=' + str(points[0])

    # Multiple Entries
    elif any(x for x in ['router_cpu', 'router_mem', 'router_temp'] if x in sensor):
        output = sensor + ' '
        output += ','.join(map('='.join, processed_data.items()))
        return output

    # Router Net
    elif 'router_net' in sensor or 'router_ping_ext' in sensor:
        output = sensor + ',' + columns[0] + '=' + str(points[0]) + ' '
        del processed_data[columns[0]]
        output += ','.join(map('='.join, processed_data.items()))
        return output

    else:
        print('UNPROCESSED ENTRIES -- %s %s' % (sensor, processed_data))


def send_payload(payload):

    # https://docs.influxdata.com/influxdb/v1.7/guides/writing_data/
    # https://docs.influxdata.com/influxdb/v1.7/tools/api/

    dbhost = '192.168.0.43:8086'
    dbname = 'router'

    cmd = ['curl', '-i', '-XPOST', 'http://' + dbhost + '/write?db=' + dbname +'&u=root&p=root', '--data-binary', payload]

    if payload:
        print(payload)
        subprocess.run(cmd)


def main():
    app = Bottle()

    @app.hook('after_request')
    def enable_cors():
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Accept, Content-Type'

    @app.route("/", method=['POST'])
    def index():

        data = json.load(request.body)
        output = convert_payload(data)
        send_payload(output)
        return 'OK'

    run(app=app, host='0.0.0.0', port=8085)


if __name__ == "__main__":
    main()
