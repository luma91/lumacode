
# Pioneer Receiver Control
import telnetlib
import time

from lumacode.get_smartdevices import rec_input

receiver_ip = '192.168.0.134'

# Volume Ranges and Remapping: MIN 045 -58 dB //// MAX = -14.5 dB / 132
low2, low1, high2, high1 = -58, 45, -14.5, 132

# -- Main Commands
POWER_ON = "PO"
POWER_OFF = "PF"
TOGGLE_MUTE = "MZ"
POWER_STATUS = "?P"
CURRENT_VOLUME = "?V"
CURRENT_INPUT = "?F"

# -- Tone Control
TONE_ON = "TO1"
TONE_BYPASS = "TO0"
TONE_QUERY = "?TO"

# -- Bass Control
BASS_INCREMENT = "BI"
BASS_DECREMENT = "BD"
BASS_QUERY = "?BA"
BASS_0DB = "BA06"
BASS_P6DB = "BA00"
BASS_N6DB = "BA12"

# -- Treble Control
TREBLE_INCREMENT = "TI"
TREBLE_DECREMENT = "TD"
TREBLE_QUERY = "?TR"
TREBLE_0DB = "TR06"
TREBLE_P6DB = "TR00"
TREBLE_N6DB = "TR12"

# -- SPEAKER SETTING
SPEAKER_OFF = "0SPK"
SPEAKER_A = "1SPK"
SPEAKER_B = "2SPK"

# -- MC Settings
MC_STATUS = "?MC"
MC_1 = "MC1"  # Less Bass
MC_2 = "MC2"  # Flat Response

# -- Listening Modes
GET_LISTENING_MODE = "?S"
PRO_LOGIC2_MOVIE = "0013SR"
AUTO_SURROUND = "0006SR"
DIRECT = "0007SR"


def delay():
    time.sleep(1)


def remap_to_db(value):
    return float(low2 + (float(value) - low1) * (high2 - low2) / (high1 - low1))


def format_command(command):
    return ("%s\r\n" % command).encode('ascii')


class Main:

    def __init__(self):

        self.telnet = None

    def start_connection(self):

        """
        Start a telnet connection with the receiver,
        3 max attempts, otherwise raise error

        """

        err = None
        for _ in range(3):

            try:
                self.telnet = telnetlib.Telnet(receiver_ip, 23, 120)

            except ConnectionRefusedError as e:

                err = e
                print('trying again.. attempt: %s' % (_ + 1))
                time.sleep(1)
                continue

            else:
                break

        else:
            raise err

    def close_connection(self):
        self.telnet.close()
        self.telnet = None

    def write_command(self, command):

        """
        For writing a command to a current connection.

        """

        self.telnet.write(format_command(command))

    def send_command(self, command):

        """
        For starting a connection and sending a command.

        """

        self.start_connection()
        self.write_command(command)
        self.close_connection()
        delay()

    def send_receive_command(self, command):

        """
        For starting a connection and sending a command, then returning the result.
        :return: string from telnet result
        """

        self.start_connection()
        self.write_command(command)
        output = self.telnet.read_until("\r\n".encode('ascii'))
        result = output.decode('ascii')
        self.close_connection()
        delay()

        return result

    def power_on(self):
        self.send_command(POWER_ON)

    def power_off(self):
        self.send_command(POWER_OFF)

    def mute(self):
        self.send_command(TOGGLE_MUTE)

    def get_power(self):
        current_power = self.send_receive_command(POWER_STATUS)
        return current_power

    def get_volume(self):
        output = self.send_receive_command(CURRENT_VOLUME)
        current_volume = float(output[3:])
        output = current_volume, remap_to_db(current_volume)
        return output

    def set_volume(self, volume):
        self.send_command("%sVL" % str(volume))

    def get_input(self):
        output = self.send_receive_command(CURRENT_INPUT)
        current_input = output.split('\r')[0].replace('FN', '')

        input_name = rec_input(operation="name", query=current_input)
        return current_input, input_name

    def set_input(self, receiver_input):

        # Get Input Code from Smart Devices List
        code = rec_input(operation="code", query=receiver_input)

        # Set Input
        self.send_command('%sFN' % code)


if __name__ == "__main__":

    rec = Main()
    # rec.send_receive_command(SPEAKER_B)
    # rec.set_input('pc')
    print(rec.get_input())
