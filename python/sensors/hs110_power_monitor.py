import pyHS100


sensors = {
    'living_room_sensor': '192.168.0.199',
    'study_sensor':  '192.168.0.153'
}


def sensor_export():

    output = {}

    for sensor in sensors:

        # Get Sensor Object:
        try:
            sensor_object = pyHS100.SmartPlug(sensors[sensor])

            consumption = sensor_object.get_emeter_realtime()
            voltage, wattage = consumption['voltage_mv'] / 1000, consumption['power_mw'] / 1000

            output.update({sensor: [voltage, wattage]})

        except Exception as e:
            print('Error: Cannot get power status on %s. %s' % (sensor, e))

    return output


if __name__ == "__main__":
    print(sensor_export())
