import pyHS100

sensor = pyHS100.SmartPlug('192.168.0.199')


def sensor_export():
    consumption = sensor.get_emeter_realtime()
    voltage, wattage = consumption['voltage_mv'] / 1000, consumption['power_mw'] / 1000
    return [voltage, wattage]


if __name__ == "__main__":
    print(sensor_export())
