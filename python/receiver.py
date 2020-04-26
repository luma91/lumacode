# Pioneer Receiver Control

import telnetlib
import get_smartdevices
receiver_ip = '192.168.0.177'
tn_in = "\r\n".encode('ascii')

# Remapping
# Protect Speakers: MIN 045 -58 dB //// MAX = -14.5 dB / 132
low2 = -58
low1 = 45
high2 = -14.5
high1 = 132


def remap_to_db(value):
    return float(low2 + (float(value) - low1) * (high2 - low2) / (high1 - low1))


class Main:

    @staticmethod
    def start_connection():
        telnet = telnetlib.Telnet(receiver_ip, 23)
        return telnet

    def send_command(self, command):
        telnet = self.start_connection()
        telnet.write((command + "\r\n").encode('ascii'))
        return telnet

    def power_on(self):
        telnet = self.send_command("PO")
        telnet.close()

    def power_off(self):
        telnet = self.send_command("PF")
        telnet.close()

    def mute(self):
        telnet = self.send_command("MZ")
        telnet.close()

    def get_power(self):
        telnet = self.send_command("?P")
        output = telnet.read_until(tn_in)
        current_power = output.decode('ascii')
        telnet.close()
        return current_power

    def get_volume(self):
        telnet = self.send_command("?V")
        current_volume = float(telnet.read_until(tn_in).decode('ascii')[3:])
        output = current_volume, remap_to_db(current_volume)
        telnet.close()
        return output

    def set_volume(self, volume):
        telnet = self.send_command(str(volume) + "VL\r\n")
        telnet.close()

    def get_input(self):

        telnet = self.start_connection()
        telnet.write("?F\r\n".encode('ascii'))
        output = telnet.read_until(tn_in)
        current_input = output.decode('ascii').split('\r')[0].replace('FN', '')

        input_name = get_smartdevices.rec_input(operation="name", query=current_input)
        return current_input, input_name

    def set_input(self, value):

        code = get_smartdevices.rec_input(operation="code", query=value)
        telnet = self.start_connection()

        if value == "pc":
            telnet.write("1SPK\r\n".encode('ascii'))
            package = (code + "FN\r\n").encode('ascii')
            telnet.write(package)

        if value == "pc2":
            telnet.write("1SPK\r\n".encode('ascii'))
            package = (code + "FN\r\n").encode('ascii')
            telnet.write(package)

        if value == "tv":
            telnet.write("1SPK\r\n".encode('ascii'))
            package = (code + "FN\r\n").encode('ascii')
            telnet.write(package)

        if value == "bedroom":
            telnet.write("2SPK\r\n".encode('ascii'))
            package = (code + "FN\r\n").encode('ascii')
            telnet.write(package)

        if value == "bedroom-hdmi":
            telnet.write("0SPK\r\n".encode('ascii'))
            package = (code + "FN\r\n").encode('ascii')
            telnet.write(package)

        if value == "headphones":
            telnet.write("0SPK\r\n".encode('ascii'))

        telnet.close()


if __name__ == "__main__":
    rec = Main()
    print(rec.get_input())
