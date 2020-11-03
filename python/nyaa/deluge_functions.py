import subprocess

server_address = "192.168.0.238"
username = "andrew"
password = "pass"


def list_torrents():

    """
    Get a list of torrents, with IDs and Torrent State (Downloading, Queued, Completed, etc..)

    """

    torrent_list = {}
    cmd = ['/bin/bash', '-c', 'deluge-console "connect %s %s %s ; info"' % (server_address, username, password)]
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
    _stdout, _stderr = proc
    output = _stdout.decode().split('\n \n')
    for obj in output:
        content = obj.split('\n')

        torrent_name = ""
        torrent_id = ""
        torrent_state = ""

        for line in content:
            if "Name" in line:
                torrent_name = line.split('Name: ')[1]

            if "ID" in line:
                torrent_id = line.split('ID: ')[1]

            if "State" in line:
                torrent_state = line.split("State: ")[1].split(' ')[0]

        torrent_list.update({torrent_name: {'torrent_id': torrent_id, 'torrent_state': torrent_state}})

    return torrent_list


def get_torrent_info(name):

    torrent_data = list_torrents()

    for torrent in torrent_data:
        if name.lower() in torrent.lower():
            return torrent, torrent_data[torrent]


def get_completed_torrents():

    """
    List all completed torrents, for removal.
    """

    output = []
    torrents = list_torrents()

    for torrent in torrents:
        torrent_data = torrents[torrent]
        torrent_state = torrent_data['torrent_state']

        if torrent_state == "Complete":
            print(torrent)
            output.append(torrent_data['torrent_id'])
        if torrent_state == "Seeding":
            print(torrent)
            output.append(torrent_data['torrent_id'])

    return output


def remove_torrent(torrent_id):
    cmd = ['/bin/bash', '-c', 'deluge-console "connect %s %s %s ; rm %s"' %
           (server_address, username, password, torrent_id)]
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
    _stdout, _stderr = proc
    output = _stdout.decode()

    print(output)


def remove_completed_torrents():

    completed_torrents = get_completed_torrents()
    for torrent in completed_torrents:
        print('removing: %s' % torrent)
        remove_torrent(torrent)


if __name__ == "__main__":
    print(get_completed_torrents())


