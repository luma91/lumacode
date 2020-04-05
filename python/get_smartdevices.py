import os
import json


def read_data():

    # Get Smart Devices
    with open(os.path.join(os.path.dirname(__file__), 'smart_devices.json'), "r") as f:
        smart_devices = json.load(f)

    return smart_devices


def address(category, name=None, zone=None):

    output = []
    smart_devices = read_data()
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


def rec_input(operation, query):

    output = None
    smart_devices = read_data()

    for cat in smart_devices:
        if cat['category'] == 'receiver_inputs':
            rec_inputs = (cat['inputs'])

            # Get Input Code
            for item in rec_inputs:

                if operation == "code":
                    if item['name'] == query:
                        return item['code']

                if operation == "name":
                    if item['code'] == query:
                        return item['name']

    return output


if __name__ == "__main__":

    # Get Smart Devices
    # media_room_camera = address(category='smartplugs', name='media_room_camera')
    # subwoofer = address(category='smartplugs', name='subwoofer')
    # print(media_room_camera, subwoofer)

    # lights = address(category='lifx', zone='media_room')  # Get Lights Data
    # print(lights)

    # Get Inputs
    x = rec_input(operation="code", query="pc2")
    print('input code: %s' % x)

    x = rec_input(operation="name", query="10FN")
    print('input name: %s' % x)
