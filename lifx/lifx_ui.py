from PyQt5 import QtWidgets, QtCore, QtGui, uic
import sys
import os

from functools import partial
from lumacode.lifx import lifx, lifx_cloud, functions, lifx_presets

base_path = os.path.dirname(__file__)
ui_path = os.path.join(base_path, 'lifx.ui')


class LifxUi(QtWidgets.QMainWindow):

    def __init__(self, parent=None):
        super(LifxUi, self).__init__(parent)
        uic.loadUi(ui_path, self)

        # Define variables
        self.lights = []
        self.groups = []
        self.protocol = None
        self.selected_group = None
        self.selected_lights = None
        self.selected_preset = None
        self.presets = {}

        self.window_title = 'Lifx Remote'

        # For preventing unwanted updates
        self._allow_change = False

        # Query Method
        dialog = QtWidgets.QDialog()
        dialog.setWindowTitle("Select a Protocol")
        dialog.setFixedWidth(400)
        dialog.setFixedHeight(100)
        dialog_layout = QtWidgets.QHBoxLayout()
        dialog.setLayout(dialog_layout)
        cloud_button = QtWidgets.QPushButton("Cloud (Default)")
        cloud_button.released.connect(partial(self.set_cloud, dialog))
        lan_button = QtWidgets.QPushButton("LAN")
        lan_button.released.connect(partial(self.set_lan, dialog))
        dialog_layout.addWidget(cloud_button)
        dialog_layout.addWidget(lan_button)
        dialog.exec()

        # Get the lights
        self.populate_ui()

        # Connect Callbacks
        self.group_listWidget.selectionModel().selectionChanged.connect(self.on_group_select)
        self.light_listWidget.selectionModel().selectionChanged.connect(self.on_light_select)
        self.presets_listWidget.selectionModel().selectionChanged.connect(self.on_preset_selection)

        # Connect Sliders
        if self.protocol == "LAN":
            self.hue_slider.valueChanged.connect(self.slider_changed)
            self.saturation_slider.valueChanged.connect(self.slider_changed)
            self.value_slider.valueChanged.connect(self.slider_changed)
            self.kelvin_slider.valueChanged.connect(self.slider_changed)

        else:
            self.hue_slider.installEventFilter(self)
            self.saturation_slider.installEventFilter(self)
            self.value_slider.installEventFilter(self)
            self.kelvin_slider.installEventFilter(self)

        # Connect Buttons
        self.power_button.released.connect(self.toggle_power)
        self.save_preset_button.released.connect(self.save_preset)
        self.delete_preset_button.released.connect(self.delete_preset)
        self.set_preset_button.released.connect(self.set_preset)

    def set_lan(self, dialog):
        self.protocol = "LAN"
        dialog.close()

    def set_cloud(self, dialog):
        self.protocol = "CLOUD"
        dialog.close()

    # ----- CALLBACKS -----

    def eventFilter(self, source, event):

        if event.type() == QtCore.QEvent.MouseMove:
            self.slider_changed(False)

        if event.type() == QtCore.QEvent.MouseButtonRelease:

            self.slider_changed(True)
            return True

        else:
            return False

    def slider_changed(self, allow_slider_update):

        # Get Values
        sat = self.saturation_slider.value()
        hue = self.hue_slider.value()
        val = self.value_slider.value()
        kelvin = self.kelvin_slider.value()

        self.hue_amount.setText(str(hue))
        self.saturation_amount.setText(str(sat))
        self.value_amount.setText(str(val))
        self.kelvin_amount.setText(str(kelvin))

        # Update color-box
        self.update_color_box()

        # Convert
        val = 0 if val == 0 else val / 100
        sat = 0 if sat == 0 else sat / 100
        kelvin = 2000 if kelvin < 2000 else int(kelvin)

        # Update Status Bar
        self.statusBar.showMessage('Hue: %s Sat: %s Val: %s Kelvin: %s' % (hue, sat, val, kelvin))

        if self.selected_lights and self._allow_change:

            if self.protocol == 'LAN' or allow_slider_update:

                # if self.protocol == "CLOUD" and len(self.selected_lights) > 1:

                #    lights = [self.get_light_by_name(x).id for x in self.selected_lights]
                #    lifx_cloud.multi_light_set(lights, hue=hue, sat=sat, br=val, ke=kelvin, duration=0.1)

                # else:

                for selected_light in self.selected_lights:

                    light = self.get_light_by_name(selected_light, get_info=False)[0]
                    light.set_hsvk(hue=hue, sat=sat, br=val, ke=kelvin, duration=0.1)

    def on_group_select(self, a, b):

        selection = a.indexes()[0]
        self.selected_group = selection
        self.populate_lights()

    def on_light_select(self, new_selection, old_selection):

        self.selected_lights = []
        self._allow_change = False

        selection = self.light_listWidget.selectionModel().selectedIndexes()

        for x in selection:
            self.selected_lights.append(x)

        # Get the light
        for selected_light in self.selected_lights:

            light, light_info = self.get_light_by_name(selected_light)

            if light:

                if len(selection) == 1:
                    self.light_name.setText(light_info['name'])

                else:
                    self.light_name.setText('Multi-Select')

                hue = light_info['hue']
                sat = light_info['sat']
                val = light_info['br']
                kelvin = light_info['kelvin']

                self.hue_slider.setValue(int(hue))
                self.saturation_slider.setValue(int(sat))
                self.value_slider.setValue(int(val))
                self.kelvin_slider.setValue(int(kelvin))

                self.hue_amount.setText(str(int(hue)))
                self.saturation_amount.setText(str(sat))
                self.value_amount.setText(str(val))
                self.kelvin_amount.setText(str(kelvin))

                # Update color-box
                self.update_color_box()

        # Connect sliders
        self._allow_change = True

    # ----- LOAD FUNCTIONS -----

    def get_lights(self, group=None):

        # Get all the lights
        if group is None:
            self.lights = lifx.get_lights(method=self.protocol)

        else:
            self.lights = lifx.get_lights(method=self.protocol, group=group)

    def populate_ui(self):

        print('protocol: %s' % self.protocol)

        if self.protocol:

            # Set Window Title
            self.setWindowTitle(self.window_title + ' — ' + self.protocol)
            self.get_lights()
            self.group_listWidget.clear()

            for light in self.lights:

                try:

                    light_info = light.get_info()

                    if light_info['group'] not in self.groups:
                        self.groups.append(light_info['group'])

                except TypeError:
                    print('error, skipping.')

            # Populate Groups widget
            for group in self.groups:
                self.group_listWidget.addItem(group)

        else:
            raise RuntimeError('You did not not specify a protocol!')

    def populate_lights(self):

        selected_group = self.selected_group.data()
        self.light_listWidget.clear()
        self.get_presets()

        # Reset query to look only at group
        if self.protocol == "LAN":
            self.lights = lifx.get_lights(method=self.protocol, group=selected_group.lower().replace(' ', '_'))

        for light in self.lights:

            light_info = light.get_info()
            if selected_group == light_info['group']:
                light_name = light_info['name']
                self.light_listWidget.addItem(str(light_name))

    # ----- PRESETS -----

    def on_preset_selection(self):

        selected_preset = self.presets_listWidget.selectionModel().selectedIndexes()

        if selected_preset:
            self.selected_preset = selected_preset[0].data()

    def get_presets(self):

        self.presets_listWidget.clear()
        selected_group = self.selected_group.data()
        presets = lifx_presets.load_presets(selected_group)

        if presets:
            for p in presets:
                QtWidgets.QListWidgetItem(str(p), parent=self.presets_listWidget)

        self.presets = presets

    def save_preset(self):

        preset_name = self.preset_name.text()
        selected_group = self.selected_group.data()

        if len(preset_name) > 0:
            print('save preset: %s' % preset_name)

            light_data = []

            for light in self.lights:
                light_info = light.get_info()
                group = light_info['group']

                if group == selected_group:
                    light_data.append(light_info)

            # Write data
            preset_name = preset_name.replace(' ', '_').lower()
            lifx_presets.write_preset(preset_name, selected_group, light_data)

            # Refresh Presets List
            self.get_presets()

    def delete_preset(self):

        print('delete preset %s' % self.selected_preset)
        selected_group = self.selected_group.data()
        lifx_presets.remove_preset(selected_group, self.selected_preset)

        # Refresh Presets List
        self.get_presets()

    def set_preset(self):

        """ For setting the lights to the selected preset """

        if self.selected_preset:
            print('setting to %s' % self.selected_preset)

            try:
                preset_data = self.presets[self.selected_preset]

                for light in self.lights:
                    light_info = light.get_info()
                    data = [x for x in preset_data if x['name'].lower().replace(' ', '_')
                            == light_info['name'].lower() and str(x['group']).lower() == light_info['group'].lower()]
                    if data:
                        data = data[0]

                        sat = data['sat']
                        br = data['br']
                        sat = float(sat / 100.0) if sat > 0 else 0
                        br = float(br / 100.0)

                        light.set_hsvk(hue=data['hue'], sat=sat, br=br, ke=data['kelvin'])

                    else:
                        print('no data?')

            except Exception as e:
                print('error: %s not valid.' % e)

        else:
            print('no selected preset.')

    def update_color_box(self):

        hue = int(round(float(self.hue_amount.text())))
        sat = int(self.saturation_amount.text()) / 100
        val = int(self.value_amount.text()) / 100
        kelvin = int(self.kelvin_amount.text())

        r, g, b = functions.convert_to_rgb((hue * 65535 / 360), (sat * 65535), (val * 65535), kelvin)
        self.set_color_box(r, g, b)

    def toggle_power(self):

        if self.selected_lights and self._allow_change:

            for selected_light in self.selected_lights:

                light = self.get_light_by_name(selected_light, get_info=False)[0]
                light.toggle_power()

    def get_light_by_name(self, selected_light, get_info=True):

        for light in self.lights:

            if get_info or self.protocol == "CLOUD":
                light_info = light.get_info()
            else:
                light_info = light.get_stored_info()

            if light_info['name'] == selected_light.data() and light_info['group'] == self.selected_group.data():
                return light, light_info

    def set_color_box(self, r, g, b):
        self.color_box.setStyleSheet('background-color: rgb(%s, %s, %s)' % (r, g, b))


def main():
    app = QtWidgets.QApplication([])
    app.setStyle(QtWidgets.QStyleFactory.create("Fusion"))
    palette = QtGui.QPalette()
    palette.setColor(QtGui.QPalette.Window, QtGui.QColor(53, 53, 53))
    palette.setColor(QtGui.QPalette.WindowText, QtCore.Qt.white)
    palette.setColor(QtGui.QPalette.Base, QtGui.QColor(25, 25, 25))
    palette.setColor(QtGui.QPalette.AlternateBase, QtGui.QColor(53, 53, 53))
    palette.setColor(QtGui.QPalette.ToolTipBase, QtCore.Qt.white)
    palette.setColor(QtGui.QPalette.ToolTipText, QtCore.Qt.white)
    palette.setColor(QtGui.QPalette.Text, QtCore.Qt.white)
    palette.setColor(QtGui.QPalette.Button, QtGui.QColor(53, 53, 53))
    palette.setColor(QtGui.QPalette.ButtonText, QtCore.Qt.white)
    palette.setColor(QtGui.QPalette.BrightText, QtCore.Qt.red)
    palette.setColor(QtGui.QPalette.Link, QtGui.QColor(42, 130, 218))

    palette.setColor(QtGui.QPalette.Highlight, QtGui.QColor(42, 130, 218))
    palette.setColor(QtGui.QPalette.HighlightedText, QtCore.Qt.black)
    palette.setColor(QtGui.QPalette.Disabled, QtGui.QPalette.ButtonText, QtCore.Qt.gray)
    palette.setColor(QtGui.QPalette.Disabled, QtGui.QPalette.WindowText, QtCore.Qt.gray)
    palette.setColor(QtGui.QPalette.Disabled, QtGui.QPalette.Text, QtCore.Qt.gray)
    palette.setColor(QtGui.QPalette.Disabled, QtGui.QPalette.Light, QtCore.Qt.darkGray)

    app.setPalette(palette)
    window = LifxUi()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
