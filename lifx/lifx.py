# Documentation
# https://github.com/mclarkk/lifxlan

import random
import threading
import time
import colorsys
import math

from lifxlan import Light, MultiZoneLight, LifxLAN
from lumacode import get_smartdevices

global continue_cycle
last_hue = 0


def get_lights_old(light_names=None, group=None):

    num_lights = 6  # Faster discovery, when specified
    lan = LifxLAN(num_lights)

    # Select by Name(s)
    if group is None:
        lights = []

        # Convert to List
        if type(light_names) is not list:
            light_names = [light_names]

        for light in light_names:

            for _ in range(5):
                try:
                    light = lan.get_device_by_name(light)
                    lights.append(light)

                except:
                    print('trying again')
                    continue

                else:
                    break

            else:
                print('cannot get light: %s' % light)

        return lights

    # Select by Group
    else:

        for _ in range(5):

            try:
                lights = lan.get_devices_by_group(group).devices

            except:
                print('trying again')
                continue

            else:
                return lights

        else:
            print('cannot get lights')


def get_lights(light_names=None, group=None):

    # Set to List
    if isinstance(light_names, list) is False:
        light_names = [light_names]

    light_objects = []

    if group:

        lights = get_smartdevices.address_new(category='lifx', zone=group)

        for light in lights:
            ip_address = light[list(light.keys())[0]]['address']
            mac = light[list(light.keys())[0]]['mac']
            light_object = Light(ip_addr=ip_address, mac_addr=mac)
            light_objects.append(light_object)

    if light_names:

        for light_name in light_names:

            lights = get_smartdevices.address_new(category='lifx', name=light_name)

            for light in lights:
                ip_address = light[light_name]['address']
                mac = light[light_name]['mac']
                light_object = Light(ip_addr=ip_address, mac_addr=mac)
                light_objects.append(light_object)

        return light_objects


def get_zones(mac, ip):

    try:
        light = MultiZoneLight(mac, ip)

        if light.supports_multizone() is True:
            color_zones = light.get_color_zones()
            return len(color_zones)

        else:
            print('not a multizone compatible light')

    except Exception as e:
        print(e)


def power_status(mac, ip):

    try:
        light = Light(mac, ip)
        power_state = light.get_power()

        return power_state

    except Exception as e:
        print(e)


def make_rgb_colour(r, g, b, k=0.5):

    """

    Return (Hue, Saturation, Brightness, Kelvin)
    Input values ranging from 0 to 1

    """

    # RGB to HSV
    hue, saturation, brightness = colorsys.rgb_to_hsv(r, g, b)

    # HSV to LIFX format
    hue = hue * 65535
    saturation = saturation * 65535
    brightness = brightness * 65535
    kelvin = 2500 + k * (9000-2500)

    return [hue, saturation, brightness, kelvin]


class Connection:

    def __init__(self, lifx_lights):

        if type(lifx_lights) is list:
            self.lifx_lights = lifx_lights
        else:
            self.lifx_lights = [lifx_lights]

    def lifx_get_values(self):

        output = ""

        for light in self.lifx_lights:
            try:
                hue, sat, br, kelvin = light.get_color()

                hue = int(hue / 65535 * 360)
                sat = int(sat / 65535 * 100)
                br = int(br / 65535 * 100)

                output = (hue, sat, br)
            except Exception as e:

                print(e)

        return output

    def toggle_power(self):

        for light in self.lifx_lights:

            try:
                power_state = light.get_power()

                if power_state == 0:
                    light.set_power(1)

                elif power_state > 0:
                    light.set_power(0)

            except Exception as e:
                print(e)

    def power_off(self):

        for light in self.lifx_lights:
            light.set_power(0)

    def power_on(self):

        for light in self.lifx_lights:
            light.set_power(65535)

    def set_rgb(self, r, g, b, duration=1):

        hue, sat, br, ke = make_rgb_colour(r, g, b)

        for light in self.lifx_lights:
            try:
                light.set_color([hue, sat, br, ke], duration=duration * 1000, rapid=False)

            except Exception as e:
                print(e)

    def set_hsv(self, hue, sat, br, ke=5000, duration=1):

        hue = (hue / 360) * 65535
        sat = sat * 65535
        br = br * 65535

        for light in self.lifx_lights:
            try:
                light.set_color([hue, sat, br, ke], duration=duration*1000, rapid=False)

            except Exception as e:
                print(e)

    def set_gradient(self, start, end, gradient_pattern='linear', duration=1):

        for light in self.lifx_lights:

            try:
                number_of_zones = len(light.get_color_zones())

                # Iterate over the zones
                last_zone = 0
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
                    color_value = make_rgb_colour(r, g, b)
                    light.set_zone_color(start_index=zone, end_index=zone, color=color_value, duration=duration*1000, rapid=False)

            except Exception as e:
                print(e)

    def color_rainbow(self, daemon, sync, interval, duration, br, sat):

        global continue_cycle
        continue_cycle = True

        for light in self.lifx_lights:
            threading.Thread(target=ColorRainbowWorker, daemon=daemon, args=(sync, light, interval, duration, br, sat)).start()

    @staticmethod
    def stop_color_rainbow():

        global continue_cycle
        continue_cycle = False

    def set_brightness(self, br):

        br = br * 65535

        try:
            for x in self.lifx_lights:
                mac, ip = x[0], x[1]
                light = Light(mac, ip)
                current_hue, current_sat, current_br, current_ke = light.get_color()
                light.set_color([current_hue, current_sat, br, current_ke], duration=.1 * 1000, rapid=False)

        except Exception as e:
            print(e)


class ColorRainbowWorker:

    global continue_cycle
    global last_hue

    def __init__(self, sync, lifx_light, interval, duration, br, sat):

        self.continue_cycle = continue_cycle
        self.last_hue = last_hue
        self.sync = sync
        self.lifx_light = lifx_light
        self.interval = interval
        self.duration = duration
        self.br = br
        self.sat = sat

        # Create Infinite Loop that doesn't die if there's a communication issue.
        while self.continue_cycle is True:

            try:
                self.worker_loop()

            except Exception as e:
                print(e)
                continue
        else:
            print("Closing Rainbow Thread")
            exit()

    def worker_loop(self):

        global continue_cycle
        random_hue = random.randint(0, 360)

        # If Last Hue is defined it means it crashed, else its a new thread!
        try:
            if self.sync is False:
                current_hue = random_hue

            else:
                current_hue = self.last_hue

        except NameError:

            if self.sync is True:
                current_hue = 0
            else:
                current_hue = random_hue

        ke = 4000
        sat = self.sat * 65535
        br = self.br * 65535

        while self.continue_cycle is True:

            self.continue_cycle = continue_cycle

            if self.lifx_light:

                current_hue += self.interval  # Amount to shift hue

                if current_hue > 360:
                    current_hue = 0

                hue = (current_hue / 360) * 65535

                # Protect against integer overflow
                if hue > 65535:
                    hue = 65535

                if self.duration > .5:
                    transition_time = self.duration

                else:
                    transition_time = .5

                self.lifx_light.set_color([hue, sat, br, ke], duration=100 + (transition_time * 1000))

                time.sleep(self.duration + .01)
                self.last_hue = current_hue


if __name__ == "__main__":

    # Power on all Media Room Lights
    # x = get_lights(['desk_strip', 'left_lamp'])
    x = get_lights(group='study')

    # x = get_lights(light_names='desk_strip')
    # print(x)

    c = Connection(x)
    c.toggle_power()
    # c.set_gradient([0, 0, .6], [.6, 0, 0], gradient_pattern='linear')

    # print(lights)

