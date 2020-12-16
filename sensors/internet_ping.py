
# https://forums.whirlpool.net.au/archive/2637720

import subprocess


def get_alive():

    cmd = ['ping', 'google.com', '-q', '-c 1']

    try:
        proc = subprocess.run(cmd, stdout=subprocess.PIPE, text=True)
        output = proc.stdout.split('\n')

    except Exception as e:

        print(e)
        return 0

    for line in output:

        # Ping was successful
        if '0% packet loss' in line:
            return 1

        # DNS Failed
        elif 'Temporary failure' in line:
            return 0

        else:
            continue

    return 0


def get_packet_loss():

    packet_loss = 0

    cmd = ['ping', 'google.com', '-q', '-c 25']
    proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    output = proc.stdout.split('\n')

    # connection error thrown, assume full packet loss.
    if proc.stderr:
        packet_loss = 100.0

    else:
        for line in output:
            if 'packet loss' in line:
                split_line = line.split(', ')
                for part in split_line:
                    if 'packet loss' in part:
                        print(part)
                        packet_loss = float(part.replace('% packet loss', ''))

    return packet_loss


def get_ping():

    data_average = 0

    # https://c.speedtest.net/speedtest-servers-static.php
    servers = [
        'speed.aussiebroadband.com.au',
        'mel1.speedtest.telstra.net',
        'speedtest.mel.optusnet.com.au',
        'geelong.vic.speedtest.optusnet.com.au'
    ]

    for server in servers:
        cmd = ['ping', server, '-q', '-c 5']
        proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        output = proc.stdout.split('\n')

        for line in output:

            # Get Ping
            if 'min/avg/max/mdev' in line:
                average = float(line.split('=')[1].split('/')[1])
                data_average += average

    data_average = float('%.2f' % (data_average / len(servers)))
    print('average ping: %s ms' % data_average)
    return data_average


if __name__ == "__main__":
    a = get_packet_loss()
    print(a)
