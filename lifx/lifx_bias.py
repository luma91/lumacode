
import colorsys
from lifxlan import *


# Find the light bulb device, establish a connection, and turn it on
def get_light(name=None):
    num_lights = 6  # Faster discovery, when specified
    lan = LifxLAN(num_lights)

    if name is not None:
        lgt = lan.get_device_by_name(name)
    else:
        devices = None
        while devices is None or len(devices) == 0:
            devices = lan.get_lights()
        lgt = devices[0]

    if lgt:
        print(f'Selected {lgt.get_label()}')
        lgt.set_power("on")

    return lgt


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


if __name__ == "__main__":
    x = get_light("Desk")
    x.set_color(make_rgb_colour(.4, 1, 1, 1), duration=1)
