# Documentation: https://api.developer.lifx.com/docs/authentication

import requests
import json

from pprint import pprint
from lumacode.lifx import constants, functions


def lifx_communicate(group=None, light_id=None, light_name=None, lights=None, payload=None):

    headers = {
        "Authorization": "Bearer %s" % constants.token,
    }

    # Request
    if payload is None:

        zone = 'group:%s' % group if group else 'all'
        return requests.get('https://api.lifx.com/v1/lights/%s' % zone, headers=headers)

    # Send
    else:

        # Group Selector
        if group:
            return requests.put('https://api.lifx.com/v1/lights/group:%s/state' % group, data=payload, headers=headers)

        # Light Specified
        if light_id:
            return requests.put('https://api.lifx.com/v1/lights/%s/state' % light_id, data=payload, headers=headers)

        if light_name:
            return requests.put('https://api.lifx.com/v1/lights/label:%s/state' % light_name, data=payload, headers=headers)

        if lights:
            print(lights)
            return requests.put('https://api.lifx.com/v1/lights/states', data=payload, headers=headers)

        # None, must be all lights?
        else:
            return requests.put('https://api.lifx.com/v1/lights/all/state', data=payload, headers=headers)


def create_payload(hue, sat, br, ke, power):

    # Keep float
    sat = 0.0 if sat == 0 else sat
    br = 0.0 if br == 0 else br

    color = "hue:%s saturation:%s kelvin:%s" % (hue, sat, ke)

    payload = {
        "color": color,
        "brightness": br,
        "power": power,
        "duration": 0.5,
        "fast": True
    }

    return json.dumps(payload)


def create_states_payload(lights, hue, sat, br, ke, power="on", duration=1.0):

    payload = {"states": []}
    color = "hue:%s saturation:%s kelvin:%s" % (hue, sat, ke)

    for light in lights:
        payload['states'].append(
            {
                "selector": "id:%s" % light,
                "color": color,
                "brightness": br,
                "power": power,
                "duration": 0.5,
                "fast": True
            }
        )

    return json.dumps(payload)


def get_lights(group=None, name=None):

    """
    Query cloud and return a dict.
    Filter by Group for faster discovery

    """

    return lifx_communicate(group=group).json()


class CustomLight:

    def __init__(self, json_data):

        # Set incoming JSON data to local
        self.id = json_data['id']

        # Static Vars
        self.name = json_data['label']
        self.group = json_data['group']['name']
        self.product = json_data['product']['name']

        # Dynamic Vars
        self.color = json_data['color']
        self.brightness = json_data['brightness']
        self.power = json_data['power']

    def get_color(self):
        return self.color['hue'], self.color['saturation'], self.brightness, self.color['kelvin']

    def get_info(self):

        hue, sat, br, kelvin = self.get_color()

        sat = int(sat * 100)
        br = int(br * 100)

        product_name = self.product
        light_type = 'strip' if 'LIFX Z' in product_name else 'lamp'

        light_data = {

            'name': self.name,
            'group': self.group,
            'light_type': light_type,
            'hue': hue,
            'sat': sat,
            'br': br,
            'kelvin': kelvin,
        }

        return light_data

    def _update_state(self):

        """ Connect to cloud and send payload """

        hue, sat, br, ke = self.get_color()
        payload = create_payload(hue, sat, br, ke, self.power)
        result = lifx_communicate(light_id=self.id, payload=payload)

        print('Name: %s, Group: %s, Payload: %s, Result: %s' % (self.name, self.group, payload, result.status_code))

    def power_on(self):

        self.power = "on"
        self._update_state()

    def power_off(self):

        self.power = "off"
        self._update_state()

    def toggle_power(self):

        if self.power == "off":
            self.power_on()

        elif self.power == "on":
            self.power_off()

    def set_hsvk(self, hue, sat, br, ke=5000, duration=1, update=True):

        self.color = {'hue': hue, 'saturation': sat, 'kelvin': ke}
        self.brightness = br

        # Send command
        if update:
            self._update_state()


def group_set(group, hue, sat, br, ke, power="on"):

    payload = create_payload(hue=hue, sat=sat, br=br, ke=ke, power=power)
    print(payload)

    result = lifx_communicate(group=group, payload=payload)
    print(result.status_code)


def multi_light_set(lights, hue, sat, br, ke, duration=1, power="on"):

    """ For multi-selection on lights (set to same value) """

    payload = create_states_payload(lights, hue=hue, sat=sat, br=br, ke=ke, duration=duration, power=power)
    pprint(payload)

    result = lifx_communicate(lights=lights, payload=payload)
    print(result.status_code)


if __name__ == "__main__":
    # multi_light_set(lights=[], hue=100, sat=0.0, br=0.3, ke=4000)
    print(get_lights('Study', name='Desk Strip'))

