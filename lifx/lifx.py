# Documentation
# https://github.com/mclarkk/lifxlan

import math

import lifxlan
from lumacode import get_smartdevices
from lumacode.lifx import functions, lifx_cloud

global continue_cycle
last_hue = 0


def truncate(v):
    return float('%.2f' % v)


def create_light_objects(light_dict):

    light_objects = []

    for light in light_dict:
        name = list(light.keys())[0]
        info = light[name]
        ip = info['address']
        mac = info['mac']
        light_info = {'name': name, 'group': info['zone'], 'light_type': info['type']}
        light_object = CustomLight(mac, ip, light_info)
        # light_object.req_with_resp(lifxlan.GetService, lifxlan.StateService)
        light_objects.append(light_object)

    return light_objects


def get_lights(light_names=None, group=None, method='LAN'):

    # Set to List
    if light_names and isinstance(light_names, list) is False:
        light_names = [light_names]

    if method == 'LAN':

        # Get Lights by Group
        if group:

            print('getting by group: %s' % group)
            lights = get_smartdevices.address_new(category='lifx', zone=group.lower())
            light_objects = create_light_objects(lights)
            return light_objects

        # Get Lights by Name
        if light_names:

            lights = []
            for light_name in light_names:
                lights.append(get_smartdevices.address_new(category='lifx', name=light_name)[0])

            light_objects = create_light_objects(lights)
            return light_objects

        # All Lights
        else:
            light_objects = create_light_objects(get_smartdevices.address_new(category='lifx'))
            return light_objects

    if method == 'CLOUD':

        lights = lifx_cloud.get_lights(group)
        result = []

        for light in lights:
            result.append(lifx_cloud.CustomLight(light))

        return result


class CustomLight(lifxlan.MultiZoneLight):

    def __init__(self, mac, ip, light_info=None):
        super(CustomLight, self).__init__(mac, ip)

        # Static Vars
        self.name = None
        self.group = None
        self.light_type = None

        # Dynamic Vars
        self.color = {'hue': 0, 'saturation': 0, 'kelvin': 0}
        self.brightness = 0

        # Get Static Info
        if light_info:
            self.name = light_info['name']
            self.group = light_info['group']
            self.light_type = light_info['light_type']

        else:
            self.get_static_info()

    def get_stored_info(self):

        light_data = {
            'name': self.name,
            'group': self.group,
            'light_type': self.light_type,
            'hue': self.color['hue'],
            'sat': self.color['saturation'],
            'br': self.brightness,
            'kelvin': self.color['kelvin'],
        }

        return light_data

    @functions.retry_on_failure()
    def get_static_info(self):

        self.name = self.get_label()
        self.group = self.get_group()
        self.light_type = 'strip' if 'LIFX Z' in self.get_product_name() else 'lamp'

    @functions.retry_on_failure()
    def get_info(self):

        """ This function will query the state of the light and update """

        hue, sat, br, kelvin = self.get_color()
        hue = int((hue / 65535) * 360)
        sat = int((sat / 65535) * 100)
        br = int((br / 65535) * 100)

        # Update Dynamic Vars
        self.color = {'hue': hue, 'saturation': sat, 'kelvin': kelvin}
        self.brightness = br

        return self.get_stored_info()

    @functions.retry_on_failure()
    def toggle_power(self):

        power_state = self.get_power()

        if power_state == 0:
            self.set_power(1)

        elif power_state > 0:
            self.set_power(0)

    @functions.retry_on_failure()
    def power_off(self):

        self.set_power(0)

    @functions.retry_on_failure()
    def power_on(self):

        self.set_power(65535)

    @functions.retry_on_failure()
    def set_rgb(self, r, g, b, duration=1):

        hue, sat, br, ke = functions.make_rgb_colour(r, g, b)
        self.set_color([hue, sat, br, ke], duration=duration * 1000, rapid=True)

    @functions.retry_on_failure()
    def set_hsvk(self, hue, sat, br, ke=5000, duration=1):

        hue = (hue / 360) * 65535
        sat = sat * 65535
        br = br * 65535
        self.set_color([hue, sat, br, ke], duration=duration*1000, rapid=True)

    @functions.retry_on_failure()
    def set_raw_hsvk(self, hue, sat, br, ke=5000, duration=1):

        """ Don't convert the values """
        self.set_color([hue, sat, br, ke], duration=duration*1000, rapid=True)

    @functions.retry_on_failure()
    def set_gradient(self, start, end, gradient_pattern='linear', duration=1):

        # Iterate over the zones
        number_of_zones = len(self.get_color_zones())
        for zone in range(number_of_zones):

            # Linear
            factor = (zone / number_of_zones)
            new_factor = factor

            if gradient_pattern == 'center':
                new_factor = factor * 2
                if new_factor > 1:
                    new_factor = factor / 2

            # Tile
            if gradient_pattern == 'tile':

                new_factor = math.sin(factor)
                print(new_factor)

            start_r = (start[0] * (1 - new_factor))
            start_g = (start[1] * (1 - new_factor))
            start_b = (start[2] * (1 - new_factor))
            end_r = (end[0] * new_factor)
            end_g = (end[1] * new_factor)
            end_b = (end[2] * new_factor)
            r = start_r + end_r
            g = start_g + end_g
            b = start_b + end_b
            color_value = functions.make_rgb_colour(r, g, b)
            self.set_zone_color(
                start_index=zone,
                end_index=zone,
                color=color_value,
                duration=duration*1000,
                rapid=True
            )

    @functions.retry_on_failure()
    def set_value(self, brightness, duration=500):
        brightness = brightness * 65535
        self.set_brightness(brightness, duration, rapid=True)


if __name__ == "__main__":

    # Power on all Media Room Lights
    # all_lights = get_lights()
    # light_addresses = get_smartdevices.address_new(category='lifx')
    # lights = get_lights(light_addresses)
    # print(light_addresses)
    lgts = get_lights(group='Study', method="CLOUD")
    for x in lgts:
        x.toggle_power()

    # c = Connection(x)
    # Nx.toggle_power()
    # print(c)

    # for lgt in all_lights:
        # lgt.power_off()
        # print(lgt.power_on())
        # lgt.set_value(0.5)
    #    print(lgt)
        # print(lgt.get_info())
        # print(x.get_group_label)
    # c.set_gradient([0, 0, .6], [.6, 0, 0], gradient_pattern='linear')

    # print(lights)

