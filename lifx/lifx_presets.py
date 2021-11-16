
import json
import os

# Specify a path for storing LIFX Presets

if os.name == "nt":
    LIFX_PRESETS = 'T:\\lifx_presets'

else:
    LIFX_PRESETS = '/mnt/tmp/lifx_presets'


def read_preset(preset_path):

    with open(preset_path, 'r') as f:
        data = json.load(f)
        return data


def remove_preset(group, preset_name):

    preset_path = os.path.join(LIFX_PRESETS, group, preset_name + '.json')
    print(preset_path)

    if os.path.exists(preset_path):
        os.remove(preset_path)


def _iterate_through_presets(presets_folder):

    preset_data = {}

    if os.path.exists(presets_folder):
        presets = os.listdir(presets_folder)

        for preset in presets:
            preset_name = os.path.splitext(preset)[0]
            full_path = os.path.join(presets_folder, preset)
            preset_data[preset_name] = read_preset(full_path)

    return preset_data


def load_presets(group=None):

    """
    Load presets by group

    """

    if group:
        group = group.lower().replace(' ', '_')

    preset_data = {}

    if os.path.exists(LIFX_PRESETS):

        if group:
            preset_data = _iterate_through_presets(os.path.join(LIFX_PRESETS, group))

        else:

            groups = os.listdir(LIFX_PRESETS)
            for group in groups:
                preset_data[group] = _iterate_through_presets(os.path.join(LIFX_PRESETS, group))

    return preset_data


def write_preset(preset_name, group, light_data, overwrite=False):

    # Check if root path exists
    if os.path.exists(LIFX_PRESETS):

        # Check if group exists
        group_path = os.path.join(LIFX_PRESETS, group.lower())
        if os.path.exists(group_path) is False:
            os.mkdir(group_path)

        light_preset = os.path.join(group_path, preset_name + '.json')

        # Prevent Overwriting
        if os.path.exists(light_preset) and overwrite is False:
            print('cannot overwrite.')

        else:
            with open(light_preset, 'w') as f:
                data = json.dumps(light_data, indent=1)
                f.write(data)


def set_preset(preset_name, group, method="LAN"):

    from lumacode.lifx import lifx

    presets = load_presets(group.lower())

    try:
        preset_data = presets[preset_name]
        lights = lifx.get_lights(group=group, method=method)

        for light in lights:
            light_info = light.get_info()

            data = [x for x in preset_data if x['name'].lower().replace(' ', '_') == light_info['name'].lower().replace(' ', '_')]

            if data:
                data = data[0]
                sat = data['sat']
                br = data['br']
                sat = float(sat / 100.0) if sat > 0 else 0
                br = float(br / 100.0)

                light.set_hsvk(hue=data['hue'], sat=sat, br=br, ke=data['kelvin'])

    except KeyError:
        print('invalid preset name?')


if __name__ == "__main__":

    presets = load_presets("study")
    for x in presets:
        print(x)
