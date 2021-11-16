
from lumacode.lifx import lifx, functions, lifx_presets
from flask import Flask, request
import json
import os
import time
import logging
import threading


logging.basicConfig(level=logging.INFO)

# Set path
os.chdir(os.path.dirname(__file__))

# Get Light Data
method = "LAN"  # CLOUD

lights = []
presets = []


def get_data():

    global lights
    global presets

    while True:
        lights = lifx.get_lights(method=method)  # CLOUD
        presets = lifx_presets.load_presets()

        time.sleep(60)


def set_light(light, field, value):

    hue, sat, br, kelvin = light.get_color()

    if method == "LAN":
        if field == 'hue':
            hue = int(int(value) / 360 * 65535)
            light.set_raw_hsvk(hue=hue, sat=sat, br=br, ke=kelvin)

        if field == 'sat':
            sat = int(int(value) / 100 * 65535)
            light.set_raw_hsvk(hue=hue, sat=sat, br=br, ke=kelvin)

        if field == 'br':
            br = int(int(value) / 100 * 65535)
            light.set_raw_hsvk(hue=hue, sat=sat, br=br, ke=kelvin)

        if field == 'ke':
            light.set_raw_hsvk(hue=hue, sat=sat, br=br, ke=int(value))

    if method == "CLOUD":
        if field == 'hue':
            hue = int(value) / 360
            light.set_hsvk(hue=hue, sat=sat, br=br, ke=kelvin)

        if field == 'sat':
            sat = int(value) / 100
            light.set_hsvk(hue=hue, sat=sat, br=br, ke=kelvin)

        if field == 'br':
            br = int(value) / 100
            light.set_hsvk(hue=hue, sat=sat, br=br, ke=kelvin)

        if field == 'ke':
            light.set_hsvk(hue=hue, sat=sat, br=br, ke=int(value))


def lifx_server():

    global lights
    global presets

    app = Flask(__name__)

    @app.route("/", methods=["GET", "POST"])
    def index():

        group = request.args.get('group')
        selected_light = request.args.get('light')

        print('selected_group: %s, selected_light: %s' % (group, selected_light))

        # Get Template
        page = open('static/templates/index.html').read()
        range_template = open('static/templates/range_template.html').read()
        page_css = 'static/css/lifx_web.css?' + str(time.time()).split('.')[0]
        content = ''

        groups = []
        for light in lights:
            if light.group not in groups:
                groups.append(light.group)

        # Light List Column
        content += '<div class="content">\n'
        content += '<div class="left">\n'

        for light_group in groups:

            css_class = 'group_link highlight' if light_group == group else 'group_link'
            content += '<div class="light_group">\n'
            content += '<div class="light_group_header"><a class="%s" href="?group=%s">%s</a></div>\n' % \
                       (css_class, light_group.replace(' ', '_'), light_group.replace('_', ' ').title())

            for light in lights:

                if light.group == light_group:
                    css_class = 'item_link highlight' if selected_light == light.name else 'item_link'
                    content += '<div class="light_item"><a class="%s" href="?group=%s&light=%s">%s</a></div>\n' % \
                               (css_class, light_group.replace(' ', '_'), light.name.replace(' ', '_'), light.name.replace('_', ' ').title())

            content += '</div>\n\n'

        content += '</div>\n\n'

        # Control Column
        content += '<div class="right">\n'

        # Update Range Template based on selection
        if selected_light:
            if method == "LAN":
                selected_light = selected_light.lower()
            else:
                selected_light = selected_light.replace('_', ' ')

        content += '<div style="display: flex;">\n'

        if selected_light:

            for light in lights:

                """ Set Sliders by Light Name"""
                if light.name == selected_light and light.group == group:
                    print(light.name)

                    content += '<div class="light_name">%s - %s</div>\n' % (str(group).replace('_', ' ').title(), str(light.name).replace('_', ' ').title())

                    # Set Ranges for selected light
                    light_info = light.get_info()
                    hue, sat, br, kelvin = light_info['hue'], light_info['sat'], light_info['br'], light_info['kelvin']
                    range_template = range_template.replace('%HUEVALUE%', str(hue))
                    range_template = range_template.replace('%SATVALUE%', str(sat))
                    range_template = range_template.replace('%BRVALUE%', str(br))
                    range_template = range_template.replace('%KEVALUE%', str(kelvin))

        elif group:
            content += '<div class="light_name">%s (Group Selected)</div>\n' % str(group).replace('_', ' ').title()

        content += '<div class="light_preview" id="light"></div>\n'
        content += '</div>\n'

        # Add range template
        content += range_template

        content += '</div>\n'

        # Power Button
        content += '<button class="power_button" type="button" onclick="toggle_power(\'%s\', \'%s\')">Toggle Power</button>' % (group, selected_light)

        content += '</div>'

        # Presets Section
        content += '<div class="light_group">\n'

        for preset_group in presets:
            preset_data = presets[preset_group]

            if preset_data:
                content += '<div class="light_group_header">%s presets</div>\n' % preset_group.replace('_', ' ').title()
                content += '<div class="light_group preset_group">\n'

                for preset in preset_data:
                    content += """
                    <div class="light_item">
                        <button class="button" type="button" onclick="set_preset(\'%s\', \'%s\')">%s</button>
                    </div>\n""" % (preset_group, preset, preset.replace('_', ' '))

                content += '</div>\n'

        content += '</div>\n\n'

        page = page.replace('${STYLESHEET_PATH}', page_css)
        page = page.replace('${PAGE_CONTENT}', content)
        return page

    @app.route("/commands", methods=["POST"])
    def commands():

        if request.method == "POST":

            # Receiver
            data = request.get_json()

            if data:

                try:
                    command_type = data.get('command_type')

                    # Convert HSV to RGB
                    if command_type == 'hsv_to_rgb':

                        hue = data.get('hue')
                        sat = data.get('sat')
                        val = data.get('br')
                        kelvin = data.get('kelvin')
                        hue, sat, val = (int(hue) * 65535 / 360), (int(sat) / 100 * 65535), (int(val) / 100 * 65535)

                        rgb = functions.convert_to_rgb(hue, sat, val, int(kelvin))
                        return json.dumps(rgb)

                    else:

                        group = data.get('group')
                        selected_light = data.get('light')
                        value = data.get('value')

                        print(group, selected_light)

                        if group:
                            if method == "LAN":
                                group = group.lower()
                            else:
                                group = group.replace('_', ' ')

                        if selected_light:
                            if method == "LAN":
                                selected_light = selected_light.lower()
                            else:
                                selected_light = selected_light.replace('_', ' ')

                        if command_type == 'set_light':

                            field = data['field']

                            # Set by group
                            if selected_light is None:

                                print('setting by group: %s' % group)

                                for light in lights:
                                    if light.group == group:
                                        set_light(light, field, value)

                            # Set by light
                            else:
                                print('setting by light: %s' % selected_light)
                                for light in lights:
                                    if light.name == selected_light and light.group == group:
                                        set_light(light, field, value)

                        if command_type == 'toggle_power':

                            if group:
                                if selected_light != 'none':
                                    print('toggling power on %s' % selected_light)
                                    for light in lights:
                                        light_info = light.get_info()
                                        if light_info['name'].lower().replace(' ', '_') == selected_light.lower().replace(' ', '_'):
                                            light.toggle_power()

                                else:
                                    print('toggling power on %s' % group)
                                    for light in lights:
                                        light_info = light.get_info()
                                        if light_info['group'].lower().replace(' ', '_') == group.lower().replace(' ', '_'):
                                            light.toggle_power()

                        # Set Preset
                        if command_type == 'preset':

                            print('setting %s to %s' % (group, value))
                            preset_data = presets[group][value]

                            for light in lights:
                                light_info = light.get_info()

                                for x in preset_data:
                                    if x['name'].lower().replace(' ', '_') == light_info['name'].lower().replace(' ', '_'):
                                        sat = x['sat']
                                        br = x['br']
                                        sat = float(sat / 100.0) if sat > 0 else 0
                                        br = float(br / 100.0)
                                        light.set_hsvk(hue=x['hue'], sat=sat, br=br, ke=x['kelvin'])

                except Exception as e:
                    logging.exception(e)
                    return str(e), 500

        # Go Back Home
        return 'OK', 200

    if os.name == "nt":
        app.run(host='127.0.0.1', port=8080)

    else:
        app.run(host='0.0.0.0', port=8080)


if __name__ == "__main__":
    t = threading.Thread(target=get_data)
    t.start()
    lifx_server()
