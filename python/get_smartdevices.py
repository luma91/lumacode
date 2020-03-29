import os
import json


def address(category, name=None, zone=None):

    # Get Smart Devices
    with open(os.path.join(os.path.dirname(__file__), 'smart_devices.json'), "r") as f:
        smart_devices = json.load(f)

    output = []

    for cat in smart_devices:

        # Filter by Category
        if category in cat['category']:

            for device in cat['devices']:

                # Search by zone
                if zone:
                    if zone in device['zone']:
                        output.append(device)

                # Search by name
                else:
                    if name in device['name']:
                        output = device['address']

    # Return the resulting address
    return output


if __name__ == "__main__":

    # Get Smart Devices
    media_room_camera = address(category='smartplugs', name='media_room_camera')
    subwoofer = address(category='smartplugs', name='subwoofer')
    print(media_room_camera, subwoofer)

    lights = address(category='lifx', zone='media_room')  # Get Lights Data
    print(lights)
