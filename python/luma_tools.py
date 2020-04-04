from pathlib import Path
import sys
import os
import subprocess
import platform
import time
import wifi370
import lifx
import lifx_presets
import json
import getpass
import atexit
import random
import pyHS100
import logging
import receiver
import get_smartdevices

# Load Qt
if "ubuntu" in platform.platform().lower() or "windows" in platform.platform().lower():
    from PyQt5 import QtWidgets, uic, QtCore, QtGui
    server_mode = False

else:
    server_mode = True

global window
global lights_op
global desk_lights
global lifx_lights
global shutdown_check
global configuration

# Get Smart Devices
media_room_camera = pyHS100.SmartPlug(get_smartdevices.address(category='smartplugs', name='media_room_camera'))
back_room_camera = pyHS100.SmartPlug(get_smartdevices.address(category='smartplugs', name='back_room_camera'))
subwoofer = pyHS100.SmartPlug(get_smartdevices.address(category='smartplugs', name='subwoofer'))

logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.INFO)
hostname = platform.node()
home_path = getpass.getuser()

# Maja's PC
if "shadow" in home_path.lower():
    lights = get_smartdevices.address(category='lifx', zone='bedroom')

else:
    lights = get_smartdevices.address(category='lifx', zone='media_room')

layout_width = 360
layout_height = 900
lowdpi_layout_height = 500
lowdpi_layout_width = 250

# UI Stuff
if server_mode is False:
    DEVNULL = open(os.devnull, 'wb')
    sys.path.append(os.path.dirname(__file__) + "/qt")
    import resources
    ui_path = os.path.dirname(__file__)
    ui_file = 'qt/luma_tools.ui'
    Ui_MainWindow, QtBaseClass = uic.loadUiType(os.path.join(ui_path, ui_file), resource_suffix='')

# Get Hostname, etc....
if "Windows" in platform.platform():
    os_version = "Windows"

else:
    platform_split = platform.platform().split("-")
    os_version = "%s %s" % (platform_split[6], platform_split[7])

print("\nHostname: %s" % hostname)
print("OS: %s" % platform.platform())
print("Username: %s\n" % home_path.title())


# Local Config
local_config_file = os.path.join(str(Path.home()), "linuxtools_config.json")


# Primary Code
class LumaTools(QtWidgets.QMainWindow, Ui_MainWindow):

    def __init__(self):

        QtWidgets.QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)

        global window
        global lights_op
        global desk_lights
        global lifx_lights
        global shutdown_check
        global configuration

        # Presets Window
        self.presets_window = PresetsWindow(self)

        self.setWindowFlags(QtCore.Qt.WindowCloseButtonHint)
        self.kill_redshift = 0

        shutdown_check = 0
        desk_lights = 0
        window = self
        lights_op = 0
        self.resize(layout_width, layout_height)

        # Update LIFX Display
        self.lifx(0)
        self.smart_lights_label.hide()

        # Turn on LIFX
        c = lifx.Connection(lights)
        lifx_lights = c.power_status()

        if lifx_lights == 0:
            lifx_lights = 1
            self.lifx(1)

        # Load Config
        configuration = local_config(0)
        atexit.register(local_config, operation=1)

        # Create Color Widget
        self.color_widget = QtWidgets.QColorDialog

        # Initial Stuff
        self.statusBar.showMessage("")
        self.vpn_status.setText('VPN: Disconnected')
        self.receiver_status.setText("Off")
        self.wifi370_layout.hide()
        self.statusBar.setSizeGripEnabled(False)

        self.primary.setContentsMargins(15, 15, 15, 15)

        # Non 4K DPI
        if high_dpi is False:
            self.resize(lowdpi_layout_height, lowdpi_layout_height)
            self.setMinimumWidth(lowdpi_layout_width)
            self.setMaximumHeight(lowdpi_layout_height)
            self.setMaximumWidth(lowdpi_layout_width)

        if lifx_lights == 0:
            self.lifx_layout.hide()

        # Maja's PC

        if "shadow" in home_path.lower():

            self.sound_desk.released.connect(lambda: self.sound_ops(0))
            self.sound_bed.released.connect(lambda: self.sound_ops(1))
            self.sound_tv.released.connect(lambda: self.sound_ops(2))

            # Hide some things
            self.light_status.hide()
            self.wifi370_toggle.hide()
            self.wifi370_layout.hide()
            self.smart_lights_label.hide()

        else:

            self.display_mirror.hide()
            self.display_restore.hide()
            self.sound_desk.hide()
            self.sound_bed.hide()
            self.sound_tv.hide()
            self.sound_label.hide()

            # Perform Check for Smart (Desk) Lights
            self.smart_lights(9)

        # Set All elements to transparent!
        self.vpn_status.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.vpn_stats_a.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.vpn_stats_b.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.sound_label.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.redshift_label.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.smart_lights_primary_label.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.light_status.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.lifx_layout.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.hue_label.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.saturation_label.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.brightness_label.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.hue_display.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.sat_display.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.br_display.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.receiver_label.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.receiver_status.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.wifi370_layout.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.wifi_r.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.wifi_g.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.wifi_b.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.wifi_v.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.vol_label.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.current_vol.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.extra_label.setAttribute(QtCore.Qt.WA_TranslucentBackground)

        # Connect Buttons ------------------------------------------------------------

        self.btn_map_wacom.released.connect(lambda: self.map_wacom())
        self.presets_button.released.connect(lambda: self.toggle_presets_window())

        # Display
        self.display_mirror.released.connect(lambda: self.display_ops(0))
        self.display_restore.released.connect(lambda: self.display_ops(1))

        # Vpn
        self.vpn_connect.released.connect(lambda: self.vpn_ops(0))
        self.vpn_disconnect.released.connect(lambda: self.vpn_ops(1))

        # Redshift
        self.redshift_disable.released.connect(lambda: self.redshift(0))
        self.redshift_slider.valueChanged.connect(lambda: self.redshift(1))

        # LIFX
        self.lifx_toggle.released.connect(lambda: self.lifx(1))
        self.lifx_toggle.released.connect(lambda: self.update_lifx())
        self.hue.sliderMoved.connect(lambda: self.lifx(3))
        self.saturation.sliderMoved.connect(lambda: self.lifx(3))
        self.light_brightness.sliderMoved.connect(lambda: self.lifx(2))

        # Wifi370
        self.wifi370_toggle.released.connect(lambda: self.smart_lights(0))
        self.smart_lights_pick_button.released.connect(lambda: self.smart_lights(2))
        self.red_slider.sliderMoved.connect(lambda: self.smart_lights(1))
        self.green_slider.sliderMoved.connect(lambda: self.smart_lights(1))
        self.blue_slider.sliderMoved.connect(lambda: self.smart_lights(1))
        self.v_slider.sliderMoved.connect(lambda: self.smart_lights(1))

        # Receiver
        self.subwoofer_toggle.released.connect(lambda: self.toggle_subwoofer())
        self.receiver_off.released.connect(lambda: self.receiver_control(1, "PF"))
        self.receiver_on.released.connect(lambda: self.receiver_control(1, "PO"))
        self.receiver_mute.released.connect(lambda: self.receiver_control(1, "MZ"))
        self.receiver_vol.sliderReleased.connect(lambda: self.receiver_control(2, 0))
        self.receiver_pc.released.connect(lambda: self.receiver_control(3, 0))
        self.receiver_pc_2.released.connect(lambda: self.receiver_control(6, 0))
        self.receiver_tv.released.connect(lambda: self.receiver_control(5, 0))
        self.receiver_headphones.released.connect(lambda: self.receiver_control(7, 0))
        self.receiver_bedroom.released.connect(lambda: self.receiver_control(4, 0))
        self.receiver_control(0, 0)

        self.camera_button.released.connect(lambda: self.camera_toggle())

        # Workstation Ops
        self.monitor_off_button.released.connect(lambda: self.monitors_off())
        self.shutdown_button.released.connect(lambda: self.shutdown_now())
        self.cgbg_button.released.connect(lambda: self.update_ui_styles())

        # WINDOWS
        if "Windows" in platform.platform():
            self.display_mirror.hide()
            self.display_restore.hide()
            self.btn_map_wacom.hide()
            self.vpn_status.hide()
            self.vpn_stats_a.hide()
            self.vpn_stats_b.hide()

        # Extra Stuff
        msg = "Initialised -- Username: %s " % home_path.title()
        self.statusBar.showMessage(msg)
        print("ready\n")
        self.update_ui_styles()

        # Setup Status Thread
        self.check_status = CheckStatus()
        self.thread1 = QtCore.QThread(self)

        self.check_receiver = CheckReceiver()
        self.thread2 = QtCore.QThread(self)

        # Connect Slots
        self.check_status.vpn_status.connect(self.update_vpn_status)
        self.check_status.vpn_stats_a.connect(self.update_vpn_stats_a)
        self.check_status.vpn_stats_b.connect(self.update_vpn_stats_b)
        self.check_status.camera_status.connect(self.update_camera_status)
        self.check_status.subwoofer_status.connect(self.update_subwoofer_status)
        self.check_receiver.receiver_status.connect(self.update_receiver_status)

        # Start Thread
        self.check_status.moveToThread(self.thread1)
        self.check_receiver.moveToThread(self.thread2)
        self.thread1.started.connect(self.check_status.main)
        self.thread1.start()

        self.thread2.started.connect(self.check_receiver.main)
        self.thread2.start()

    @QtCore.pyqtSlot(int)
    def update_vpn_status(self, connected):

        if connected == 1:
            self.vpn_status.setText("VPN: Connected")
            self.vpn_status.setStyleSheet("color:rgb(70, 180, 25);")
            self.vpn_stats_b.show()

        else:
            self.vpn_status.setText("VPN: Disconnected")
            self.vpn_status.setStyleSheet("color:rgb(100, 100, 100);")
            self.vpn_stats_a.setText("")
            self.vpn_stats_b.setText("")
            self.vpn_stats_b.hide()

    @QtCore.pyqtSlot(str)
    def update_vpn_stats_a(self, stats):
        self.vpn_stats_a.setText(stats)

    @QtCore.pyqtSlot(str)
    def update_vpn_stats_b(self, stats):
        self.vpn_stats_b.setText(stats)
        self.vpn_stats_b.setMaximumHeight(30)

    @QtCore.pyqtSlot(int)
    def update_camera_status(self, status):

        if status == 1:
            self.camera_status.setText("On")
            self.camera_status.setStyleSheet("color:rgb(30, 150, 30);")

        else:
            self.camera_status.setText("Off")
            self.camera_status.setStyleSheet("color:rgb(70, 70, 70);")

    @QtCore.pyqtSlot(int)
    def update_receiver_status(self, status):

        if status == 1:
            self.receiver_status.setText("On")
            self.receiver_status.setStyleSheet("color:rgb(30, 150, 30);")

        else:
            self.receiver_status.setText("Off")
            self.receiver_status.setStyleSheet("color:rgb(70, 70, 70);")

    @QtCore.pyqtSlot(int)
    def update_subwoofer_status(self, status):

        if status == 1:
            self.subwoofer_status.setText("On")
            self.subwoofer_status.setStyleSheet("color:rgb(30, 150, 30);")

        else:
            self.subwoofer_status.setText("Off")
            self.subwoofer_status.setStyleSheet("color:rgb(70, 70, 70);")

    def update_ui_size(self, height, width):

        self.resize(width, height)
        self.setMaximumHeight(height)

    def update_ui_styles(self):

        background_image = ''
        bg_image_dir = os.path.join(os.path.dirname(__file__), 'images', 'bg')
        random_number = random.randint(1, len(os.listdir(bg_image_dir)))
        num = 1

        for i in os.listdir(bg_image_dir):
            if num == random_number:
                background_image = os.path.join(bg_image_dir, i)
            num += 1

        if "Windows" in os_version:
            background_image = background_image.replace('\\', '/')

        print("Background Chosen: %s" % background_image)

        # Font Hack
        if high_dpi is False:
            font_size = '9pt'
        else:
            font_size = '8pt'

        global_styles = (

                # Defaults
                '*{ color:#bbb; font-size: ' + font_size + ';}' +
                '.QWidget{border-image: url(\'' + background_image + '\') 0 450 0 0; }' +
                '.QFrame{background-color: rgba(15, 15, 15, 200);}' +
                '.QPushButton{background-color: #151515; color:#ddd; margin: 3px; height: 35px;}' +
                # '.QLabel{margin:5px;}' +
                '.QStatusBar{font-size: 7pt;}' +
                '.QPushButton:hover{background-color:#444;}' +

                # Sliders
                'QSlider::groove:horizontal {background: #555; height: 10px;} ' +
                'QSlider::sub-page:horizontal {background: qlineargradient( x1: 0, y1: 0, x2: 1, y2: 1, stop: 0 #444, stop: 1 #999); height: 10px;}' +
                'QSlider::add-page:horizontal {background: #2a2a2a; height: 10px;}'
                'QSlider::handle:horizontal {background: #555; width: 13px; margin-top: -2px; margin-bottom: -2px;}' +
                'QSlider::handle:horizontal:hover {background: #777;}'
                'QSlider {margin-left: 2px;}'
        )

        receiver_zone_stylesheet = '.QPushButton{background-color: #003;} .QPushButton:hover{background-color:#444;}'
        self.receiver_bedroom.setStyleSheet(receiver_zone_stylesheet)
        self.receiver_pc.setStyleSheet(receiver_zone_stylesheet)
        self.receiver_headphones.setStyleSheet(receiver_zone_stylesheet)
        self.receiver_pc_2.setStyleSheet(receiver_zone_stylesheet)
        self.receiver_tv.setStyleSheet(receiver_zone_stylesheet)

        # Non 4K DPI
        # https://stackoverflow.com/questions/16613505/setting-layout-margins-in-pyqt
        if high_dpi is False:
            global_styles += '.QPushButton{height: 23px;  margin: 3px;}'
            self.vpn_master_layout.setContentsMargins(15, 10, 15, 0)
            self.reciever_vol_layout.setContentsMargins(0, 0, 0, 0)
            self.redshift_layout.setContentsMargins(5, 0, 5, 5)
            self.sound_layout.setContentsMargins(5, 0, 5, 5)
            self.primary_layout.setSpacing(0)

        # Set Stylesheet
        self.setStyleSheet(global_styles)
        self.redshift_disable.setStyleSheet('font-size: 7pt;')
        self.receiver_mute.setStyleSheet('font-size: 7pt;')
        self.current_vol.setStyleSheet('font-size: 8pt; color:rgb(140, 140, 140); padding-left: 4px; padding-right: 4px;')

    # LAYOUT ONLY
    def update_lifx(self):

        global lifx_lights

        if lifx_lights == 0:
            self.lifx_layout.show()
            self.lifx_label.show()
            lifx_lights = 1

            if screen_height is False:
                self.update_ui_size(lowdpi_layout_width, lowdpi_layout_height + 100)

        else:
            self.lifx_layout.hide()
            self.lifx_label.hide()
            lifx_lights = 0

            if screen_height is False:
                self.update_ui_size(lowdpi_layout_width, lowdpi_layout_height)

    def toggle_presets_window(self):
        self.presets_window.hide()
        self.presets_window.show()

    @staticmethod
    def monitors_off():

        if "Windows" not in platform.platform():
            subprocess.Popen(['/bin/bash', '-c', 'xset dpms force off'], shell=False)

        else:
            nircmd(command="monitor off")

    def smart_lights(self, mode):

        global desk_lights

        re = self.red_slider.value() / 100
        gr = self.green_slider.value() / 100
        bl = self.blue_slider.value() / 100
        v = self.v_slider.value() / 100

        # Load Saved State
        if mode == 9:
            desk_light_config = configuration['desk_lights']
            power = desk_light_config['power']

            re, gr, bl, v = (
                desk_light_config['r'],
                desk_light_config['g'],
                desk_light_config['b'],
                desk_light_config['v']
            )

            self.red_slider.setValue(int(re))
            self.green_slider.setValue(int(gr))
            self.blue_slider.setValue(int(bl))
            self.v_slider.setValue(int(v))

            if power == 0:
                self.wifi370_layout.hide()

                if screen_height is False:
                    self.update_ui_size(lowdpi_layout_width, lowdpi_layout_height)
                else:
                    self.update_ui_size(layout_width, layout_height)

                desk_lights = 0
                window.light_status.setText('Desk Lights Off')

            else:
                self.wifi370_layout.show()

                if screen_height is False:
                    self.update_ui_size(lowdpi_layout_width, lowdpi_layout_height + 100)
                else:
                    self.update_ui_size(layout_width, layout_height + 150)

                desk_lights = 1
                window.light_status.setText('Desk Lights On')

        # Toggle Power
        if mode == 0:
            if desk_lights == 0:
                window.light_status.setText('Desk Lights On')
                self.wifi370_layout.show()
                self.smart_lights_label.show()

                if screen_height is False:
                    self.update_ui_size(lowdpi_layout_width, lowdpi_layout_height + 100)
                else:
                    self.update_ui_size(layout_width, layout_height + 150)

                self.smart_lights(1)
                desk_lights = 1

            elif desk_lights == 1:
                c = wifi370.Connection()
                msg = ">> %s" % c.turn_off()
                print(msg)
                self.statusBar.showMessage(msg)
                window.light_status.setText('Desk Lights Off')
                self.wifi370_layout.hide()
                self.smart_lights_label.hide()

                if screen_height is False:
                    self.update_ui_size(lowdpi_layout_width, lowdpi_layout_height)
                else:
                    self.update_ui_size(layout_width, layout_height)

                desk_lights = 0

        # Slider Method
        if mode == 1:
            c = wifi370.Connection()

            window.light_status.setText('Desk Lights On')

            msg = ">> %s" % c.color(v, re, gr, bl)
            print(msg)
            self.statusBar.showMessage(msg)

        # Color Picker Method
        if mode == 2:

            c = wifi370.Connection()

            custom_color = QtGui.QColor().fromRgb(re * 255, gr * 255, bl * 255)
            color = self.color_widget.getColor(custom_color)

            if color.isValid():

                re = float("%.2f" % (color.red() / 255))
                gr = float("%.2f" % (color.green() / 255))
                bl = float("%.2f" % (color.blue() / 255))
                v = float("%.2f" % (color.value() / 255))

                if v > .99:
                    v = .99

                self.red_slider.setValue(re * 100)
                self.green_slider.setValue(gr * 100)
                self.blue_slider.setValue(bl * 100)
                self.v_slider.setValue(v * 100)

                msg = c.color(v, re, gr, bl)
                print(msg)
                self.statusBar.showMessage(msg)

    def lifx(self, operation):

        hue = self.hue.value()
        sat = self.saturation.value()
        br = self.light_brightness.value()

        self.hue_display.setText(str(hue))
        self.sat_display.setText(str(sat))
        self.br_display.setText(str(br))

        c = lifx.Connection(lights)

        # Get Status
        if operation == 0:
            try:
                hue, sat, br = c.lifx_get_values()
                print("Hue: %s Saturation: %s Brightness %s" % (hue, sat, br))

                self.hue_display.setText(str(hue))
                self.sat_display.setText(str(sat))
                self.br_display.setText(str(br))
                self.hue.setValue(hue)
                self.saturation.setValue(sat)
                self.light_brightness.setValue(br)

            except ValueError:
                pass

        # Toggle Power
        if operation == 1:
            c.toggle_power()

        # Change Brightness
        if operation == 2:

            try:
                msg = ">> LIFX Lights set to: " + str(br) + "%"
                print(msg)
                self.statusBar.showMessage(msg)
                br = br / 100
                c.set_brightness(br)

            except Exception as e:
                print(e)
                self.statusBar.showMessage(">> Too many packets sent!")

        # Change Hue / Sat
        if operation == 3:

            try:
                msg = ">> LIFX Lights - Hue: " + str(hue) + " Sat: " + str(sat) + "%"
                print(msg)
                self.statusBar.showMessage(msg)
                sat = sat / 100
                br = br / 100
                c.set_color(hue, sat, br, 0)

            except Exception as e:
                print(e)
                self.statusBar.showMessage(">> Too many packets sent!")

        # Force Update of UI
        self.repaint()

    def map_wacom(self):

        if "workstation" not in hostname.lower():
            subprocess.Popen(['xsetwacom', 'set', 'Wacom Cintiq 13HD Pen stylus', 'MapToOutput', 'HEAD-0'], shell=False)
        else:
            subprocess.Popen(['xsetwacom', 'set', 'Wacom Intuos4 8x13 Pen stylus', 'MapToOutput', 'HEAD-0'],
                             shell=False)

        msg = "\n>> Mapped Wacom Tablet to Primary Display."

        print(msg)
        self.statusBar.showMessage(msg)

    def display_ops(self, mode):

        if mode == 0:
            subprocess.Popen(["/home/" + home_path + '/Documents/shell_scripts/mirror_displays.sh'])
            msg = "\n>> Mirror Displays"

        if mode == 1:
            subprocess.Popen(["/home/" + home_path + '/Documents/shell_scripts/restore_displays.sh'])
            msg = "\n>> Restore Displays"

        print(msg)
        self.statusBar.showMessage(msg)

    def sound_ops(self, mode):

        if mode == 0:
            if "Windows" not in platform.platform():
                subprocess.Popen(['/bin/sh', '-c', 'pacmd "set-card-profile 0 off"'])
                subprocess.Popen(['/bin/sh', '-c', 'pacmd "set-card-profile 1 off"'])
                subprocess.Popen(['/bin/sh', '-c', 'pacmd "set-card-profile 2 output:analog-stereo"'])
            else:
                nircmd(command="setdefaultsounddevice \"Speakers\" 1")

            msg = ">> Sound Desk"

        if mode == 1:
            if "Windows" not in platform.platform():
                subprocess.Popen(['/bin/sh', '-c', 'pacmd "set-card-profile 0 off"'])
                subprocess.Popen(['/bin/sh', '-c', 'pacmd "set-card-profile 1 off"'])
                subprocess.Popen(['/bin/sh', '-c', 'pacmd "set-card-profile 2 output:iec958-stereo"'])
            else:
                nircmd(command="setdefaultsounddevice \"Digital Audio (S/PDIF)\" 1")

            msg = ">> Sound Bed"

        if mode == 2:
            if "Windows" not in platform.platform():
                subprocess.Popen(['/bin/sh', '-c', 'pacmd "set-card-profile 1 off"'])
                subprocess.Popen(['/bin/sh', '-c', 'pacmd "set-card-profile 2 off"'])
                subprocess.Popen(['/bin/sh', '-c', 'pacmd "set-card-profile 0 output:hdmi-stereo-extra1"'])
            else:
                nircmd(command="setdefaultsounddevice \"Cintiq 13HD\" 1")

            msg = ">> Sound TV"

        print(msg)
        self.statusBar.showMessage(msg)

    def vpn_ops(self, mode):

        if mode == 0:

            if "Windows" in platform.platform():
                cmd = '\"C:/Program Files (x86)/NordVPN/NordVPN.exe\" -cn \"Singapore #209\"'
                print(cmd)
                subprocess.Popen(cmd)

            else:
                window.vpn_status.setText('VPN: Connecting...')
                window.vpn_status.setStyleSheet("color:rgb(190, 150, 30);")
                subprocess.Popen(['/bin/bash', '-c', 'nordvpn connect singapore'], shell=False)

            msg = ">> Connecting VPN"
            print(msg)
            self.statusBar.showMessage(msg)

        if mode == 1:
            msg = ">> Disconnecting VPN"
            print(msg)
            self.statusBar.showMessage(msg)

            if "Windows" in platform.platform():
                subprocess.Popen(['C:/Program Files (x86)/NordVPN/NordVPN.exe', '-d'])

            else:
                window.vpn_status.setText('VPN: Disconnecting...')
                window.vpn_stats_a.setText('')
                subprocess.Popen(['/bin/bash', '-c', 'nordvpn disconnect'], shell=False)

            self.vpn_status.setStyleSheet("color:rgb(190, 150, 30);")

            # Reset Network
            if "shadow" in home_path.lower():
                script_path = os.path.split(__file__)[0]
                python_path = sys.executable
                c = python_path, os.path.join(script_path, 'reset_network.py')
                subprocess.Popen(c, shell=False)

            # msg = "Reset Network Adapter"
            print(msg)
            self.statusBar.showMessage(msg)

    def redshift(self, mode):

        redshift_path_windows = "C:/_etc/redshift.exe"

        # Kill Redshift
        if self.kill_redshift == 0:
            self.kill_redshift = 1
            if "Windows" in platform.platform():
                pass
            else:
                subprocess.Popen(['/bin/bash', '-c', 'killall redshift'], shell=False)

        if mode == 0:
            if "Windows" in platform.platform():
                pass
            else:
                subprocess.Popen(['/bin/bash', '-c', 'redshift -P -x'], shell=False)
            self.redshift_slider.setValue(0)

        if mode == 1:
            redshift_amount = self.redshift_slider.value()
            redshift_c = int(5000 * (1 - (redshift_amount / 100)) + 1600)
            redshift_b = '%.2f' % (1 * (1 - ((redshift_amount / 100) * .75)))

            if "Windows" in platform.platform():
                subprocess.Popen([redshift_path_windows, '-P', '-O' + str(redshift_c), ' -b ' + str(redshift_b)],
                                 shell=False)
            else:
                subprocess.Popen(['/bin/bash', '-c', 'redshift -P -O '
                                  + str(redshift_c) + ' -b ' + str(redshift_b)], shell=False)

            msg = '>> Redshift Set to K' + str(redshift_c) + " B" + str(redshift_b)
            print(msg)
            self.statusBar.showMessage(msg)

        # Force Update of UI
        self.repaint()

    def camera_toggle(self):

        if media_room_camera.state == "ON":
            media_room_camera.turn_off()
            back_room_camera.turn_off()
            window.camera_status.setText("Off")
            window.camera_status.setStyleSheet("color:rgb(70, 70, 70);")

        else:
            media_room_camera.turn_on()
            back_room_camera.turn_on()
            window.camera_status.setText("On")
            window.camera_status.setStyleSheet("color:rgb(30, 150, 30);")

        msg = "Camera Power Toggle"
        print(msg)
        self.statusBar.showMessage(msg)

    def toggle_subwoofer(self):

        if subwoofer.state == "ON":
            subwoofer.turn_off()
            window.subwoofer_status.setText("Off")
            window.subwoofer_status.setStyleSheet("color:rgb(70, 70, 70);")
        else:
            subwoofer.turn_on()
            window.subwoofer_status.setText("On")
            window.subwoofer_status.setStyleSheet("color:rgb(30, 150, 30);")

        msg = ">> Toggle Subwoofer Power"
        print(msg)
        self.statusBar.showMessage(msg)

    def receiver_control(self, mode, command):

        try:
            rec = receiver.Main()
            msg = ""

            # Query Current Status, Update Display, etc..
            if mode == 0:

                # Get Volume
                current_volume = rec.get_volume()

                self.receiver_vol.setValue(current_volume[0])
                self.current_vol.setText(str(current_volume[1]) + " dB")

            # Toggle Power / Mute
            if mode == 1:

                if command == "MZ":
                    msg = ">> Toggle Mute"
                    rec.mute()

                else:

                    if command == "PO":
                        msg = ">> Power On Receiver"
                        self.receiver_status.setText("On")
                        self.receiver_status.setStyleSheet("color:rgb(30, 150, 30);")
                        rec.power_on()

                    if command == "PF":
                        msg = ">> Power Off Receiver"
                        self.receiver_status.setText("Off")
                        self.receiver_status.setStyleSheet("color:rgb(70, 70, 70);")
                        rec.power_off()

            # Set Volume
            if mode == 2:

                new_volume = self.receiver_vol.value()

                if new_volume <= 133:

                    # Hack for Adding 0
                    if new_volume < 100:
                        new_volume = str("0" + str(new_volume))

                    db = rec.remap_to_db(value=new_volume)

                    msg = (">> Setting Vol to: " + str(new_volume)) + " | " + str(db) + " dB"
                    self.current_vol.setText(str(db) + " dB")
                    rec.set_volume(new_volume)

            # Get Zone Code:
            # telnet.write("?F\r\n".encode('ascii'))
            # output = telnet.read_until(tn_in)
            # current_zone = output.decode('ascii')
            # msg = "Current Receiver Zone Code: %s" % current_zone

            # Set to Media Room
            if mode == 3:
                rec.set_input(value='pc')
                msg = ">> Receiver Zone: PC 1"

                if "Windows" not in platform.platform():
                    # subprocess.Popen(['/bin/sh', '-c', 'pacmd "set-card-profile 0 off"'])
                    # subprocess.Popen(['/bin/sh', '-c', 'pacmd "set-card-profile 1 off"'])
                    # subprocess.Popen(['/bin/sh', '-c', 'pacmd "set-card-profile 2 output:iec958-stereo"'])

                    subprocess.Popen(['/bin/sh', '-c', 'pacmd "set-card-profile 1 output:iec958-stereo"'])
                    subprocess.Popen(['/bin/sh', '-c', 'pacmd "set-card-profile 0 output:iec958-stereo"'])

                else:
                    nircmd(command="setdefaultsounddevice \"Digital Audio (S/PDIF)\" 1")

            # Set to Bedroom
            if mode == 4:
                rec.set_input(value='bedroom')
                msg = ">> Receiver Zone: Bed Room"

            # Set to TV
            if mode == 5:
                rec.set_input(value='tv')
                msg = ">> Receiver Zone: TV"

            # Set to PC 2
            if mode == 6:
                rec.set_input(value='pc2')
                msg = ">> Receiver Zone: PC 2"

            if mode == 7:
                rec.set_input(value='headphones')
                subwoofer.turn_off()

                msg = ">> Receiver Zone: Headphones"

            # Update Status
            print(msg)
            self.statusBar.showMessage(msg)

            # Force Update of UI
            self.repaint()

        except ConnectionRefusedError:
            print("Could not communicate with receiver!")

    def shutdown_now(self):
        global shutdown_check
        global desk_lights

        if shutdown_check == 1:
            print("Emergency Shutdown!")

            # Shutdown Devices
            try:
                c = wifi370.Connection()
                c.turn_off()
                self.receiver_control(1, "PF")
                c = lifx.Connection(lights)
                c.power_off()

            except Exception as e:
                print(e)

            # Save Config
            try:
                desk_lights = 0
                local_config(1)
                time.sleep(.5)

            except Exception as e:
                print(e)

            # Shutdown System
            if "Windows" in platform.platform():
                os.system('shutdown -s -t 1')
            else:
                os.system('shutdown now')

        else:
            msg = ">> Press shutdown again to shutdown!"
            self.shutdown_button.setStyleSheet("background-color:rgb(90, 10, 0);")
            shutdown_check = 1
            print(msg)
            self.statusBar.showMessage(msg)

    def closeEvent(self, event):

        # local_config(1)
        event.accept()  # let the window close


class PresetsWindow(QtWidgets.QMainWindow):

    def __init__(self, parent):

        self.parent = parent

        QtWidgets.QWidget.__init__(self)
        self.setWindowTitle("Presets Window")
        self.setStyleSheet("background-color: #222; color: #fff;")

        if screen_height is False:
            self.setFixedSize(450, 80)
        else:
            self.setFixedSize(650, 100)

        widget = QtWidgets.QWidget(self)
        self.setCentralWidget(widget)

        primary_layout = QtWidgets.QVBoxLayout()
        widget.setLayout(primary_layout)

        layout_01 = QtWidgets.QHBoxLayout()  # Row 1
        layout_02 = QtWidgets.QHBoxLayout()  # Row 2

        # Add Buttons
        movie_preset = QtWidgets.QPushButton('Movie')
        warm_preset = QtWidgets.QPushButton('Warm')
        bright_preset = QtWidgets.QPushButton('Bright')
        purple_preset = QtWidgets.QPushButton('Purple')
        blue_preset = QtWidgets.QPushButton('Blue')
        preset_01 = QtWidgets.QPushButton('Preset 1')
        slow_rainbow_preset = QtWidgets.QPushButton('Slow Rainbow')
        party_preset = QtWidgets.QPushButton('Party')

        layout_01.addWidget(movie_preset)
        layout_01.addWidget(warm_preset)
        layout_01.addWidget(purple_preset)
        layout_01.addWidget(blue_preset)

        layout_02.addWidget(preset_01)
        layout_02.addWidget(slow_rainbow_preset)
        layout_02.addWidget(party_preset)
        layout_02.addWidget(bright_preset)

        primary_layout.addLayout(layout_01)
        primary_layout.addLayout(layout_02)

        # Connect Buttons
        movie_preset.released.connect(lambda: self.set_preset("movie"))
        warm_preset.released.connect(lambda: self.set_preset("warm"))
        bright_preset.released.connect(lambda: self.set_preset("bright"))
        purple_preset.released.connect(lambda: self.set_preset("purple"))
        blue_preset.released.connect(lambda: self.set_preset("blue"))
        preset_01.released.connect(lambda: self.set_preset("preset_01"))
        slow_rainbow_preset.released.connect(lambda: self.set_preset("slow_rainbow"))
        party_preset.released.connect(lambda: self.set_preset("party"))

    def set_preset(self, preset):

        color = lifx_presets.main(preset)

        # Update UI
        if color:
            self.parent.red_slider.setValue(color[1] * 100)
            self.parent.green_slider.setValue(color[2] * 100)
            self.parent.blue_slider.setValue(color[3] * 100)
            self.parent.v_slider.setValue(color[0] * 100)

        print("Set Preset: %s" % preset.title())


def local_config(operation):
    global window
    global configuration
    global desk_lights

    # Read Configuration
    if operation == 0:

        if os.path.exists(local_config_file) is False:

            print("local config not found. creating a new config file.")
            configuration = {"config": {}, "desk_lights": {"power": "off", "r": "0", "g": "0", "b": "0", "v": "0"}}

            with open(local_config_file, "w") as f:
                json.dump(configuration, f)

        else:
            print("local config found.")
            with open(local_config_file, "r") as f:
                configuration = json.load(f)

        return configuration

    else:
        print("updating config")

        # Get New Data

        re = window.red_slider.value()
        gr = window.green_slider.value()
        bl = window.blue_slider.value()
        v = window.v_slider.value()

        configuration['desk_lights']['power'] = desk_lights
        configuration['desk_lights']['r'] = re
        configuration['desk_lights']['g'] = gr
        configuration['desk_lights']['b'] = bl
        configuration['desk_lights']['v'] = v

        with open(local_config_file, "w") as f:
            json.dump(configuration, f)


def nircmd(command):
    nircmd_path = 'C:/_etc/nircmdc.exe'
    cmd = nircmd_path + " " + command
    subprocess.Popen(cmd)


class CheckReceiver(QtCore.QObject):

    receiver_status = QtCore.pyqtSignal(int)
    receiver_vol = QtCore.pyqtSignal(float)
    current_vol = QtCore.pyqtSignal(str)

    def main(self):

        while True:

            try:

                # Check Receiver Status
                rec = receiver.Main()
                current_power = rec.get_power()

                if "PWR0" in current_power:
                    self.receiver_status.emit(1)

                    # Update Volume
                    time.sleep(.5)
                    current_volume = rec.get_volume()
                    self.receiver_vol.emit(current_volume[0])
                    self.current_vol.emit(str(current_volume[1]) + " dB")

                elif "PWR1" in current_power:
                    self.receiver_status.emit(0)

            except Exception as e:

                logging.error(e)
                print("Error checking receiver. Will try again shortly.")

            # General Wait Period
            time.sleep(10)


class CheckStatus(QtCore.QObject):

    subwoofer_status = QtCore.pyqtSignal(int)
    camera_status = QtCore.pyqtSignal(int)

    vpn_status = QtCore.pyqtSignal(int)
    vpn_stats_a = QtCore.pyqtSignal(str)
    vpn_stats_b = QtCore.pyqtSignal(str)

    def main(self):

        while True:

            try:

                # Check Sub Power:
                if subwoofer.state == "ON":
                    self.subwoofer_status.emit(1)

                else:
                    self.subwoofer_status.emit(0)

                # Check Camera Power:
                if media_room_camera.state == "ON":
                    self.camera_status.emit(1)

                else:
                    self.camera_status.emit(0)

                # Check VPN
                if "Windows" not in platform.platform():
                    p = subprocess.Popen(['/bin/sh', '-c', 'nordvpn status'], stdout=subprocess.PIPE,
                                         stderr=subprocess.PIPE)
                    out, err = p.communicate()

                    filtered_output = out.decode('UTF-8').split('\n')

                    for i in filtered_output:
                        if "Country" in i:
                            country = i.split(": ")[1].replace(" ", "")
                            self.vpn_stats_a.emit("%s" % country)

                        if "ip:" in i.lower():
                            ip_addr = i.split(": ")[1]
                            self.vpn_stats_b.emit("Public IP Address: %s" % ip_addr)

                    if "Connected" in out.decode('UTF-8'):

                        # VPN Connected
                        self.vpn_status.emit(1)

                    else:
                        try:
                            # VPN Disconnected
                            self.vpn_status.emit(0)

                        except NameError:
                            pass

            except Exception as e:

                logging.error(e)
                print("Error checking stuff. Will try again shortly.")

            # General Wait Period
            time.sleep(5)


if __name__ == '__main__':

    if server_mode is False:
        app = QtWidgets.QApplication(sys.argv)
        screen_resolution = app.desktop().screenGeometry()
        screen_width, screen_height = screen_resolution.width(), screen_resolution.height()

        if screen_width < 3840:
            high_dpi = False
        else:
            high_dpi = True

        print("Resolution: %sx%s" % (screen_width, screen_height))

        window = LumaTools()
        window.setAttribute(QtCore.Qt.WA_TranslucentBackground, True)
        window.show()

        sys.exit(app.exec_())
