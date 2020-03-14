# Documentation
# https://github.com/mclarkk/lifxlan

import lifxlan as lifx
import time
import random
import threading
import get_smartdevices

global continue_cycle
last_hue = 0


class Connection:

    def __init__(self, lifx_lights):

        lifx_lights_ip = []
        lifx_lights_newmac = []

        for x in lifx_lights:
            ip = x['address']
            mac = x['mac']
            lifx_lights_ip.append(ip)
            lifx_lights_newmac.append(mac)

        self.lifx_lights = zip(lifx_lights_newmac, lifx_lights_ip)

    def power_status(self):

        for x in self.lifx_lights:
            try:
                mac, ip = x[0], x[1]
                light = lifx.Light(mac, ip)
                power_state = light.get_power()

                return power_state

            except Exception as e:
                print(e)

    def lifx_get_values(self):

        output = ""

        for x in self.lifx_lights:
            try:
                mac, ip = x[0], x[1]
                light = lifx.Light(mac, ip)
                hue, sat, br, kelvin = light.get_color()

                hue = int(hue / 65535 * 360)
                sat = int(sat / 65535 * 100)
                br = int(br / 65535 * 100)

                output = (hue, sat, br)
            except Exception as e:
                print(e)

        return output

    def toggle_power(self):

        for x in self.lifx_lights:
            try:
                mac, ip = x[0], x[1]
                light = lifx.Light(mac, ip)
                power_state = light.get_power()

                if power_state == 0:
                    light.set_power(1)

                elif power_state == 65535:
                    light.set_power(0)

            except Exception as e:
                print(e)

    def power_off(self):

        for x in self.lifx_lights:
            mac, ip = x[0], x[1]
            light = lifx.Light(mac, ip)
            light.set_power(0)

    def power_on(self):

        for x in self.lifx_lights:
            mac, ip = x[0], x[1]
            light = lifx.Light(mac, ip)
            light.set_power(65535)

    def set_hue(self, hue):

        hue = (hue / 360) * 65535

        for x in self.lifx_lights:
            try:
                mac, ip = x[0], x[1]
                light = lifx.Light(mac, ip)
                light.set_hue(hue)

            except Exception as e:
                print(e)

    def set_color(self, hue, sat, br, ke):

        hue = (hue / 360) * 65535
        sat = sat * 65535
        br = br * 65535

        for x in self.lifx_lights:
            try:
                mac, ip = x[0], x[1]
                light = lifx.Light(mac, ip)
                light.set_color([hue, sat, br, ke])
            except Exception as e:
                print(e)

    def color_fade(self, hue, sat, br, ke, duration):

        hue = (hue / 360) * 65535
        sat = sat * 65535
        br = br * 65535

        for x in self.lifx_lights:
            mac, ip = x[0], x[1]
            light = lifx.Light(mac, ip)
            light.set_color([hue, sat, br, ke], duration=duration*1000, rapid=False)

    def color_rainbow(self, daemon, sync, interval, duration, br, sat):

        global continue_cycle
        continue_cycle = True

        for light in self.lifx_lights:
            threading.Thread(target=self.ColorRainbowWorker, daemon=daemon, args=(sync, light, interval, duration, br, sat)).start()

    @staticmethod
    def stop_color_rainbow():

        global continue_cycle
        continue_cycle = False

    @staticmethod
    class ColorRainbowWorker:

        global continue_cycle
        global last_hue

        def __init__(self, sync, light, interval, duration, br, sat):

            self.continue_cycle = continue_cycle
            self.last_hue = last_hue
            self.sync = sync
            self.light = light
            self.interval = interval
            self.duration = duration
            self.br = br
            self.sat = sat

            # Create Infinite Loop that doesn't die if there's a communication issue.
            while continue_cycle is True:

                try:
                    self.worker_loop()

                except Exception as e:
                    print(e)
                    continue
            else:
                print("Closing Rainbow Thread")
                exit()

        def worker_loop(self):

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

            x = self.light
            ke = 4000
            sat = self.sat * 65535
            br = self.br * 65535

            while continue_cycle is True:

                mac, ip = x[0], x[1]
                light = lifx.Light(mac, ip)

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

                light.set_color([hue, sat, br, ke], duration=100 + (transition_time * 1000))

                time.sleep(self.duration + .01)
                self.last_hue = current_hue

    def set_brightness(self, br):

        br = br * 65535

        try:
            for x in self.lifx_lights:
                mac, ip = x[0], x[1]
                light = lifx.Light(mac, ip)
                current_hue, current_sat, current_br, current_ke = light.get_color()
                light.set_color([current_hue, current_sat, br, current_ke], duration=.1 * 1000, rapid=False)

        except Exception as e:
            print(e)


if __name__ == "__main__":

    # Power on all Media Room Lights
    c = Connection(get_smartdevices.address(category='lifx', zone='media_room'))
    c.set_brightness(.3)

