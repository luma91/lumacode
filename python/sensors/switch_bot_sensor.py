# https://github.com/bbostock/Switchbot_Py_Meter
from __future__ import print_function
import datetime
from bluepy import btle
import os

import logging
logging.basicConfig(level=logging.INFO)


# Modify the following for your setup....
meters = [
    {'name': 'living_room', 'mac': 'de:5b:6d:46:96:21'},
    {'name': 'study', 'mac': 'e7:27:36:07:b5:b7'},
]


class ScanProcessor:

    def __init__(self, json_export_path):
        self.connected = False
        self.json_export_path = json_export_path

    def handleDiscovery(self, dev, isNewDev, isNewData):

        try:
            for m in meters:

                if dev.addr.lower() in m['mac']:

                    for (sdid, desc, value) in dev.getScanData():

                        # Model T (WOSensorTH) example Service Data: 000d54006400962c
                        if desc == '16b Service Data':
                            if value.startswith('000d'):
                                byte2 = int(value[8:10], 16)
                                battery = (byte2 & 127)
                                byte3 = int(value[10:12], 16)
                                byte4 = int(value[12:14], 16)
                                byte5 = int(value[14:16], 16)
                                tempc = float(byte4 - 128) + float(byte3 / 10.0)
                                humidity = byte5

                                self._publish(m['name'], tempc, humidity, battery)

        except Exception as e:
            logging.error(e)

    def _publish(self, room, tempc, humidity, battery):

        now = datetime.datetime.now()
        topic = '{}'.format(room.lower())
        time_now = now.strftime("%Y-%m-%d %H:%M:%S")
        msgdata = '{"sensor_name": \"' + topic + '\", "time": \"' + time_now + '\", "temperature": ' + str(tempc) + ', "humidity": ' + str(
            humidity) + ', "battery": ' + str(battery) + '}'

        path = os.path.join(self.json_export_path, room + '.json')
        with open(path, 'w+') as outfile:
            outfile.write(msgdata)
            
        logging.debug(msgdata)


def main(json_export_path):
    scanner = btle.Scanner().withDelegate(ScanProcessor(json_export_path))
    devices = scanner.scan(5)


if __name__ == "__main__":
    main('/mnt/tmp/')
