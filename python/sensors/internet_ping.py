# https://forums.whirlpool.net.au/archive/2637720

import subprocess


def main():

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
                print(result)

    data_average = data_average / len(servers)
    print('average: %.2f ms' % data_average)

    return data, data_average


if __name__ == "__main__":
    main()
