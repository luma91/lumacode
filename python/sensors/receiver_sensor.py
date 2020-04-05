import os
import sys
import time

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))


def get_receiver_state():

    import receiver

    rec = receiver.Main()
    current_power = rec.get_power()

    if "PWR0" in current_power:
        power_state = 1

    else:
        power_state = 0

    time.sleep(.5)
    current_volume = rec.get_volume()[1]
    time.sleep(.5)
    current_input = rec.get_input()[1]

    return {'power': power_state, 'vol': current_volume, "input": current_input}


if __name__ == "__main__":
    a = main()
    print(a)
