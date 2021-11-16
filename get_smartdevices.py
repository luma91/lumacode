import json
import os


def read_data():

    # Get Smart Devices
    with open(os.path.join(os.path.dirname(__file__), 'smart_devices.json'), "r") as f:
        smart_devices = json.load(f)

    return smart_devices


def address_new(category, zone=None, light_type=None, name=None):

    output_list = []
    smart_devices = read_data()

    for cat in smart_devices:
        if category in cat['category']:

            for devices in cat['devices']:

                for device in devices:

                    if name:
                        if name in device:
                            output_list.append({device: devices[device]})

                    # Zone
                    elif zone:
                        if zone in devices[device]['zone']:

                            # Zone and Type
                            if light_type:
                                if light_type in devices[device]['type']:
                                    output_list.append({device: devices[device]})

                            # Zone Only
                            else:
                                output_list.append({device: devices[device]})

                    # Type Only
                    elif light_type:
                        if light_type in devices[device]['type']:
                            output_list.append({device: devices[device]})

                    # Nothing specified, get all devices
                    else:
                        output_list.append({device: devices[device]})

    return output_list


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


def get_receiver_inputs():

    output = []
    smart_devices = read_data()

    for cat in smart_devices:
        if cat['category'] == 'receiver_inputs':
            rec_inputs = cat['inputs']

            for item in rec_inputs:
                output.append(item['name'])

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

    lights = address_new(category='lifx')  # Get Lights Data
    print(lights)

    # Get Inputs
    # x = rec_input(operation="code", query="pc2")
    # print('input code: %s' % x)

    # x = rec_input(operation="name", query="10FN")
    # print('input name: %s' % x)

    # x = get_receiver_inputs()
    # print(x)
