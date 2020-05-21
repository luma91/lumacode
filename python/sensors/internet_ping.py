# https://forums.whirlpool.net.au/archive/2637720

import subprocess


def get_alive():

    connected = 0
    cmd = ['ping', 'google.com', '-q', '-c 1']
    proc = subprocess.run(cmd, stdout=subprocess.PIPE, text=True)
    output = proc.stdout.split('\n')

    for line in output:

        # Ping was successful
        if '0% packet loss' in line:
            return 1

        # DNS Failed
        elif 'Temporary failure in name resolution' in line:
            return 0

        else:
            continue

    return connected


def get_ping():

    data = []
    data_average = 0

    # https://c.speedtest.net/speedtest-servers-static.php
    servers = [
        'speedtest.mel01.softlayer.com',
        'mel1.speedtest.telstra.net',
        'speed.aussiebroadband.com.au',
        'speedtest.mel.optusnet.com.au',
        'geelong.vic.speedtest.optusnet.com.au'
    ]

    for server in servers:
        cmd = ['ping', server, '-q', '-c 5']
        proc = subprocess.run(cmd, stdout=subprocess.PIPE, text=True)
        output = proc.stdout.split('\n')

        for line in output:
            if 'min/avg/max/mdev' in line:
                average = float(line.split('=')[1].split('/')[1])
                result = (server, line, average)
                data.append(result)
                data_average += average

    data_average = float('%.2f' % (data_average / len(servers)))
    print('average: %s ms' % data_average)

    return data_average


if __name__ == "__main__":
    a = get_ping()
    print(a)
