import lifx
import wifi370
import get_smartdevices


def main(preset, zone='media_room'):

    preset = preset.lower()
    lights = get_smartdevices.address(category='lifx', zone=zone)

    c = lifx.Connection([lights[0], lights[1]])
    c2 = lifx.Connection([lights[2]])
    c3 = lifx.Connection([lights[3], lights[4]])
    color = None
    duration = 1

    c.stop_color_rainbow()

    if preset == "bright":
        c.color_fade(hue=0, sat=0, br=1, ke=4000, duration=duration)

        if "media_room" == zone:
            c2.color_fade(hue=0, sat=0, br=1, ke=4000, duration=duration)
            c3.color_fade(hue=0, sat=0, br=1, ke=4000, duration=duration)

            color = [.95, 1, .7, .5]

    elif preset == "warm":
        c.color_fade(hue=0, sat=.05, br=.18, ke=2000, duration=duration)

        if "media_room" == zone:
            c2.color_fade(hue=0, sat=.05, br=.3, ke=2000, duration=duration)
            c3.color_fade(hue=0, sat=.05, br=.3, ke=2000, duration=duration)

            color = [0.15, .6, .25, 0]

    elif preset == "purple":
        c.color_fade(hue=300, sat=1, br=.35, ke=5000, duration=duration)

        if "media_room" == zone:
            c2.color_fade(hue=300, sat=1, br=.5, ke=5000, duration=duration)
            c3.color_fade(hue=300, sat=1, br=.5, ke=5000, duration=duration)

            color = [.4, .5, 0, .6]

    elif preset == "blue":
        c.color_fade(hue=200, sat=1, br=.3, ke=5000, duration=duration)

        if "media_room" == zone:
            c2.color_fade(hue=200, sat=1, br=.5, ke=5000, duration=duration)
            c3.color_fade(hue=200, sat=1, br=.5, ke=5000, duration=duration)

        color = [.17, 0, 0.15, 1]

    elif preset == "preset_01":
        c.color_fade(hue=200, sat=1, br=.5, ke=5000, duration=duration)

        if "media_room" == zone:
            c2.color_fade(hue=300, sat=1, br=.5, ke=5000, duration=duration)
            c3.color_fade(hue=300, sat=1, br=.5, ke=5000, duration=duration)

        color = [.25, 0.35, 0, 1]

    elif preset == "movie":

        c.color_fade(hue=340, sat=0.3, br=.1, ke=1000, duration=duration)

        if "media_room" == zone:
            c2.color_fade(hue=340, sat=0.3, br=.25, ke=1000, duration=duration)
            c3.color_fade(hue=360, sat=1, br=.1, ke=1000, duration=duration)

            color = [.1, .5, .2, 0.1]

    elif preset == "slow_rainbow":

        if "media_room" == zone:
            c = lifx.Connection(lights)

        c.color_rainbow(interval=2, duration=1.5, br=.6, sat=.85, sync=True, daemon=0)

    elif preset == "party":

        if "media_room" == zone:
            c = lifx.Connection(lights)
            w = wifi370.Connection()
            w.builtin_color_cycle()

        c.color_rainbow(interval=5, duration=.25, br=.9, sat=.9, sync=False, daemon=0)

    if color:
        w = wifi370.Connection()
        w.color(color[0], color[1], color[2], color[3])
        return color

    else:
        return None


if __name__ == "__main__":
    main('warm')
