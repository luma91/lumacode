# https://github.com/kyb3r/dhooks
import static_sensors
import time
from dhooks import Webhook

# List for storing most recent alerts
recent_alerts = []
clear_alerts = 0


# Function to Read Sensors and determine if to send a message
def main():

    global clear_alerts
    global recent_alerts

    while True:

        try:
            sensor_data = static_sensors.main()
            for sensor in sensor_data:

                sensor_name = sensor.replace('_', ' ')
                state = sensor_data[sensor]

                # VPN & Camera Alerts
                if any(x for x in ["vpn", "camera"] if x in sensor):

                    if state == 0:
                        alert = "%s has been disconnected!" % sensor_name
                        send_alert(sensor, state, alert)

            # Temperature Alerts

            # Power Alerts

        except Exception as e:
            print(e)

        # Default waiting period
        time.sleep(10)
        clear_alerts += 1

        # Clear alerts after an hour.
        if clear_alerts == 360:
            recent_alerts = []


def send_alert(sensor, state, alert):

    global recent_alerts

    webhook_url = "https://discordapp.com/api/webhooks/686122353737990145/mFcWLAegamXt2C58RFKTvDdu4twCHPSf8Amv2Wv5pMdrL1Oe253Hw1-OQxTucIBDsvAt"

    # Check against recent alerts
    if alert not in recent_alerts[-3:]:

        # Check if alert is still valid (wait 10 seconds)
        time.sleep(10)

        try:
            sensor_data = static_sensors.main()

            if sensor_data[sensor] == state:

                hook = Webhook(webhook_url)
                hook.send(alert)

                recent_alerts.append(alert)
                print('Sending Message: "%s"' % alert)

            else:
                print('Alert no longer valid. Skipping: %s' % sensor)

        except Exception as e:
            print(e)

        # Waiting period before checking for another alert
        time.sleep(30)


if __name__ == "__main__":
    main()
