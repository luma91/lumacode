import pyHS100


sensors = {
    'living_room_sensor': '192.168.0.199',
    'study_sensor':  '192.168.0.153',
    'shadow_sensor': '192.168.0.215'
}


def energy_calculator(w, h=24):

    rate = 0.2123
    kwh = float(w * h / 1000)

    return [round(kwh, 3), round(kwh * rate, 2)]


def sensor_export():

    output = {}

    for sensor in sensors:

        voltage, wattage = [0, 0]

        # Get Sensor Object:
        try:
            sensor_object = pyHS100.SmartPlug(sensors[sensor])
            consumption = sensor_object.get_emeter_realtime()
            voltage, wattage = consumption['voltage_mv'] / 1000, consumption['power_mw'] / 1000

        except Exception as e:
            print('Error: Cannot get power status on %s. %s' % (sensor, e))

        finally:
            energy = energy_calculator(wattage)
            output.update({sensor: {'volts': voltage, 'watts': wattage, 'kwh': energy[0], 'day_rate': energy[1]}})

    return output


if __name__ == "__main__":
    print(sensor_export())
