
from lumacode.lifx import lifx

presets = [
    "bright", "warm", "purple", "bright_blue", "blue", "aqua", "bright_red", "red",
    "preset_01", "preset_02", "preset_03", "preset_04", "preset_05", "movie", "slow_rainbow",
    "party"
]


def main(preset, zone='Study'):

    preset = preset.lower()

    if preset == "slow_rainbow":
        lights = lifx.get_lights(group=zone)
        c = lifx.Connection(lights)
        c.color_rainbow(interval=2, duration=1.5, br=.6, sat=.85, sync=True, daemon=0)

    elif preset == "party":
        lights = lifx.get_lights(group=zone)
        c = lifx.Connection(lights)
        c.color_rainbow(interval=5, duration=.25, br=.9, sat=.9, sync=False, daemon=0)

    else:

        if zone == 'Study':
            strips = lifx.Connection(lifx.get_lights('desk_strip'))
            lamps = lifx.Connection(lifx.get_lights(['left_lamp']))

        else:
            strips = lifx.Connection(lifx.get_lights(['couch_strip', 'tv_strip']))
            lamps = lifx.Connection(lifx.get_lights('side_lamp', 'couch_lamp'))

        # Make sure they are on
        strips.power_on()
        lamps.power_on()

        if preset == "bright":
            strips.set_hsv(hue=0, sat=0, br=1, ke=4000)
            lamps.set_hsv(hue=0, sat=0, br=1, ke=4000)

        elif preset == "warm":
            strips.set_hsv(hue=0, sat=.05, br=.18, ke=2000)
            lamps.set_hsv(hue=0, sat=.05, br=.3, ke=2000)

        elif preset == "work":
            strips.set_hsv(hue=0, sat=0.01, br=.25, ke=3500)
            lamps.set_hsv(hue=0, sat=0.01, br=.4, ke=3500)

        elif preset == "purple":
            strips.set_hsv(hue=300, sat=1, br=.35)
            lamps.set_hsv(hue=300, sat=1, br=.5)

        elif preset == "bright_blue":
            strips.set_hsv(hue=240, sat=1, br=1)
            lamps.set_hsv(hue=240, sat=1, br=1)

        elif preset == "blue":
            strips.set_hsv(hue=240, sat=1, br=.3)
            lamps.set_hsv(hue=240, sat=1, br=.3)

        elif preset == "aqua":
            strips.set_hsv(hue=180, sat=1, br=.5)
            lamps.set_hsv(hue=190, sat=1, br=.4)

        elif preset == "bright_red":
            strips.set_hsv(hue=360, sat=1, br=1)
            lamps.set_hsv(hue=360, sat=1, br=1)

        elif preset == "red":
            strips.set_hsv(hue=360, sat=1, br=.3)
            lamps.set_hsv(hue=360, sat=1, br=.3)

        elif preset == "preset_01":
            strips.set_hsv(hue=200, sat=1, br=.5)
            lamps.set_hsv(hue=300, sat=1, br=.4)

        elif preset == "preset_02":
            strips.set_hsv(hue=50, sat=.7, br=.4)
            lamps.set_hsv(hue=350, sat=.65, br=.3)

        elif preset == "preset_03":
            strips.set_hsv(hue=120, sat=.95, br=.5)
            lamps.set_hsv(hue=230, sat=.75, br=.4)

        elif preset == "preset_04":
            strips.set_gradient([0, 0, .6], [.6, 0, 0], gradient_pattern='linear')
            lamps.set_hsv(hue=230, sat=.75, br=.4)

        elif preset == "preset_05":
            strips.set_gradient([.4, 0, 0], [0, 0, .6], gradient_pattern='linear')
            lamps.set_hsv(hue=270, sat=.8, br=.3)

        elif preset == "movie":
            strips.set_hsv(hue=0, sat=.85, br=.05, ke=2000)
            lamps.set_hsv(hue=0, sat=.5, br=.05, ke=2000)


if __name__ == "__main__":
    main('warm')
