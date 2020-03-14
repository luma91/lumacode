import socket
import time
import colorsys
import threading

wifi370_ip = '192.168.0.136'


class Connection:

    def __init__(self):

        host = wifi370_ip
        port = 5000

        # Connect
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.connect((host, port))
        self.default_timeout = .01

    def turn_on(self):
        time.sleep(self.default_timeout)
        command = "9d 62 06 00 00 00 60 f0 f0 f0 00 00 f0 f0 f0 40 10 10 10 06"
        msg = bytes.fromhex(command)
        self.s.send(msg)
        self.s.close()
        return "Sending Turn On Command."

    def turn_off(self):
        time.sleep(self.default_timeout)
        command = "9d 62 06 00 00 00 60 f0 f0 f0 00 00 f0 f0 f0 40 00 10 10 05"
        msg = bytes.fromhex(command)
        self.s.send(msg)
        return "Sending Turn Off Command."

    def color(self, v, re, ge, bl):
        time.sleep(self.default_timeout)
        re2 = abs(int(128 * re) - 4)
        ge2 = abs(int(128 * ge) - 4)
        bl2 = abs(int(128 * bl) - 4)
        v2 = int(240 * v)
        v2 = '{:02x} '.format(v2)
        rgb = '{:02x} {:02x} {:02x}'.format(re2, ge2, bl2)
        command = "9d 62 06 00 00 00 " + v2 + rgb + " 00 00 00 00 00 40 10 10 10 06"
        msg = bytes.fromhex(command)
        self.s.send(msg)
        return "Setting Color to V: " + str(v) + " R: " + str(re) + " G: " + str(ge) + " B: " + str(bl)

    def builtin_color_cycle(self):
        # speed = "f0"  # Slow
        speed = "f0"
        command = "9d 62 00 00 00 00 00 00 00 00 00 " + speed + " 02 01 00 00 10 20 10 02"
        msg = bytes.fromhex(command)
        self.s.send(msg)

    def color_cycle(self, hue, v, speed, daemon):
        threading.Thread(target=self.color_cycle_worker, daemon=daemon, args=(hue, v, speed)).start()

    def color_cycle_worker(self, hue, v, speed):

        current_hue = hue
        sat = .85

        while True:

            if current_hue >= 360:
                current_hue = 0

            color_rgb = colorsys.hsv_to_rgb(h=current_hue / 360, s=sat, v=1)

            time.sleep(self.default_timeout)
            re2 = abs(int(128 * color_rgb[0]) - 4)
            ge2 = abs(int(128 * color_rgb[1]) - 4)
            bl2 = abs(int(128 * color_rgb[2]) - 4)
            v2 = int(240 * v)
            v2 = '{:02x} '.format(v2)
            rgb = '{:02x} {:02x} {:02x}'.format(re2, ge2, bl2)
            command = "9d 62 06 00 00 00 " + v2 + rgb + " 00 00 00 00 00 40 10 10 10 06"
            msg = bytes.fromhex(command)
            self.s.send(msg)

            current_hue += .5
            time.sleep(.5)
            print(current_hue)

    def disconnect(self):
        self.s.close()


if __name__ == "__main__":
    c = Connection(wifi370_ip, 5000)
    # c.color_cycle(hue=0, v=.2, speed=1, daemon=False)
    c.builtin_color_cycle()
    # c.disconnect()
