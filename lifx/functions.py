
import colorsys
from lumacode.lifx import kelvin_to_rgb


def retry_on_failure(default_value='', attempts=5):

    """

    LIFX will have an issue on some device, whether its connecting or getting a value,
    this will allow us to retry without crashing the entire program.

    """

    def decorator(func):

        def new_func(*args, **kwargs):

            for _ in range(attempts):
                try:
                    return func(*args, **kwargs)

                except Exception as e:

                    print('error: %s' % e)
                    continue

        return new_func

    return decorator


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


def convert_to_rgb(h, s, v, k=0.5):

    """

    FOR PREVIEW / SWATCHES, etc..

    """

    # HSV to LIFX format
    h = h / 65535
    s = s / 65535
    v = v / 65535

    # Remap value from linear to sRGB for better preview
    if v > 0.0031308:
        v = 1.055 * (pow(v, (1.0 / 2.4))) - 0.055
    else:
        v = 12.92 * v

    # HSV to RGB, convert to 8 bit.
    r, g, b = colorsys.hsv_to_rgb(h, s, v)
    r = int(r * 255)
    g = int(g * 255)
    b = int(b * 255)

    kr, kg, kb = kelvin_to_rgb.convert(k)
    kr, kg, kb = int(kr) * v, int(kg) * v, int(kb) * v

    r = (r * s) + kr * (1 - s)
    g = (g * s) + kg * (1 - s)
    b = (b * s) + kb * (1 - s)

    # return [truncate(r), truncate(g), truncate(b)]
    return [int(r), int(g), int(b)]
