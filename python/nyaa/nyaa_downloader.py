import urllib.request
import os
import sys
import platform
from xml.dom import minidom
import json

platform_os = platform.platform()
base_path = os.path.dirname(__file__)
sys.path.append(os.path.join(base_path, '..'))

# ------------------------------------------
# Paths below! --------------

website = "https://nyaa.si/?page=rss"  # This is the usual path for nyaa
base_directory = "/mnt/ds918-Media/.temp"  # Where I have mounted on my PC
base_directory_nas = "/volume1/Media/.temp"  # Path for my Synology NAS
flags = "&c=1_2&f=0"  # These do something, I'm totally sure of it...
video_quality = "1080p"
ignore_flags = ["mini", "batch", "batched", "NoobSubs", "Where", "Hardsub", "60FPS"]  # Keywords to ignore when scanning.


# Change your OS depending on what you use for Front End
if "Ubuntu" in platform_os:
    from PyQt5 import QtWidgets, uic, QtCore, QtGui
    nas_mode = 0
    discord = 0
    plex_directory = "/mnt/Media/Anime"
    directory = base_directory

else:
    
    # Ubuntu VM (for Discord Bot)
    nas_mode = 1

    if "Ubuntu-18.04" in platform_os:
        plex_directory = "/mnt/Media/Anime"
        directory = base_directory
        discord = 1
        sys.path.append(os.path.join(os.path.dirname(__file__), '../discord_bot'))
        import discord_bot

    # Synology NAS
    else:
        plex_directory = "/volume1/Media/Anime"
        directory = base_directory_nas
        discord = 0

torrent_dir = os.path.join(directory, "transmission/watch")
download_dir = os.path.join(directory, "transmission/completed")
show_database = os.path.join(directory, "show_database.json")

# ------------------------------------------

# Get Logger
import luma_log
logger = luma_log.main(__file__)


def run_scan(a):

    logger.info("Scanning: " + a['name'])
    a_filtered = str(a['name']).replace(" ", "+")
    url = (website + "&q=" + a_filtered + "+" + str(a['subgroup']) + "+" + video_quality + flags)

    # Exception for Sub HD.
    if "no" in a['fullhd'].lower():
        url = (website + "&q=" + a_filtered + "+" + str(a['subgroup']) + "+" + flags)

    logger.info(url)
    page = urllib.request.urlopen(url)
    page_data = page.read()
    xml_doc = minidom.parseString(page_data)
    item_list = xml_doc.getElementsByTagName("item")

    title_list = []
    link_list = []
    seeders_list = []
    size_list = []

    for item in item_list:
        title = item.getElementsByTagName("title")[0].childNodes
        link = item.getElementsByTagName("link")[0].childNodes
        seeders = item.getElementsByTagName("nyaa:seeders")[0].childNodes
        size = item.getElementsByTagName("nyaa:size")[0].childNodes

        for i in title:
            i = i.data.replace(" / ", " - ")  # Filter for stupid groups that put / in the filename.
            title_list.append(i)

        for i in link:
            link_list.append(i.data)

        for i in seeders:
            seeders_list.append(i.data)

        for i in size:
            size_list.append(i.data)

    parsed_shows_list = zip(title_list, link_list, seeders_list, size_list)
    return parsed_shows_list

# Main UI Code (Front End)
if nas_mode is 0:

    sys.path.append(os.path.dirname(__file__))
    import resources
    ui_path = os.path.dirname(__file__)
    ui_file = 'nyaa.ui'
    Ui_MainWindow, QtBaseClass = uic.loadUiType(os.path.join(ui_path, ui_file), resource_suffix='')

    # If database doesn't exist, make a new one.
    if os.path.exists(show_database) is False:
        with open(show_database, "w") as f:
            data = {}
            json.dump(data, f)

    download_list = {}

    # Define Window Class
    class NyaaDownloader(QtWidgets.QMainWindow, Ui_MainWindow):

        def __init__(self):

            global download_list
            download_list = []

            # Initialize UI
            QtWidgets.QMainWindow.__init__(self)
            Ui_MainWindow.__init__(self)
            self.setupUi(self)

            # UI Stuff
            self.addnew_button.released.connect(self.add_new)
            self.remove_button.released.connect(self.remove)
            self.scan_button.released.connect(self.start_scan)
            self.download_button.released.connect(self.download)
            self.scan_progress.hide()
            self.update_showtree()
            self.download_button.setEnabled(0)

            self.show_tree.setColumnWidth(0, 80)
            self.show_tree.setColumnWidth(1, 75)
            self.show_tree.setColumnWidth(2, 170)

            # Setup Scan Thread
            self.scan_shows = ScanShows()
            self.thread1 = QtCore.QThread(self)
            self.scan_shows.update_progress.connect(self.update_progress)
            self.scan_shows.update_available_tree.connect(self.update_available_tree)
            self.scan_shows.moveToThread(self.thread1)
            self.thread1.started.connect(self.scan_shows.main)

        def start_scan(self):
            self.thread1.start()

        def update_showtree(self):
            self.show_tree.clear()

            with open(show_database, "r") as f:
                shows = json.load(f)

            current_id = 1
            for a in shows:
                qt_item = QtWidgets.QTreeWidgetItem(self.show_tree)
                qt_item.setText(0, str(current_id))
                qt_item.setText(1, str(a['fullhd']))
                qt_item.setText(2, str(a['subgroup']))
                qt_item.setText(3, str(a['name']))
                current_id += 1

        @QtCore.pyqtSlot(str)
        def update_available_tree(self, title):
            qt_item = QtWidgets.QTreeWidgetItem(self.available_tree)
            qt_item.setText(0, str(title))

        @QtCore.pyqtSlot(int)
        def update_progress(self, progress):

            if progress == 0:
                self.download_button.setEnabled(0)
                self.download_button.setStyleSheet('')
                self.available_tree.clear()  # We have just started scan, clean up the list.
                self.scan_progress.show()

            elif progress == 100:
                self.scan_progress.setValue(progress)
                logger.info("Scan Complete!")
                self.thread1.exit()     # Scan is complete. exit scanning thread.

                if len(download_list) > 0:
                    self.download_button.setEnabled(1)
                    self.download_button.setStyleSheet('background-color: #052;')
                else:
                    self.download_button.setEnabled(0)
                    qt_item = QtWidgets.QTreeWidgetItem(self.available_tree)
                    qt_item.setText(0, str("No new episodes found..."))
                    logger.info("No new episodes found")

            self.scan_progress.setValue(progress)

        def download(self):

            for title in download_list:
                torrent_file = os.path.join(torrent_dir, title + ".torrent")
                try:
                    torrent = urllib.request.urlretrieve(download_list[title], torrent_file)
                    logger.debug(torrent)
                    logger.info("Downloading: %s" % title)

                except Exception as e:
                    if discord is 1:
                        discord_bot.message("I couldn't download %s. :(" % title)  # Message Discord Chat of Failure.
                    logger.error(e)

                # c = ['konsole', '-e', 'ktorrent \"' + torrent_file + '\" --silent']
                # subprocess.Popen(c, shell=False)

            self.download_button.setEnabled(0)
            message_text = "The torrents should now be on the NAS!"
            logger.info(message_text)

            msg = QtWidgets.QMessageBox(self)
            msg.setText(message_text)
            msg.setWindowTitle("Hello!")
            msg.show()

        def add_new(self):

            dlg = QtWidgets.QInputDialog(self)
            dlg.setInputMode(QtWidgets.QInputDialog.TextInput)
            dlg.setWindowTitle("Add new show")
            dlg.setLabelText("Format: Subgroup, Show Name")
            dlg.setTextValue("HorribleSubs, ")
            dlg.resize(500, 100)
            ok = dlg.exec_()
            value = dlg.textValue()

            if ok and len(value) > 1:

                # Open Database and check for shows
                with open(show_database, "r") as f:
                    shows = json.load(f)

                try:
                    value = value.split(", ")
                    num = len(shows) + 1
                    data_formatted = {'name': value[1], 'subgroup': value[0], 'fullhd': 'yes'}
                    shows.append(data_formatted)

                    if len(value[0]) > 1 and len(value[1]) > 1:

                        with open(show_database, "w") as f:
                            json.dump(shows, f, indent=2)

                        sanitized_path = value[1].strip()
                        show_path = os.path.join(plex_directory, sanitized_path)
                        logger.info("Added new show: " + value[1])
                        logger.info("Attempting to make directory in Plex: " + show_path)
                        os.mkdir(show_path)
                        self.update_showtree()

                    else:
                        logger.error("You didn't really put anything in did you...\n")

                except IndexError:

                    logger.error("Error: Using wrong formatting!\n")

        def remove(self):

            # Get selected item
            selection = self.show_tree.currentItem().data(3, 0)
            logger.info("Sel ID: " + str(selection))

            with open(show_database, "r") as f:
                shows = json.load(f)

            msg = ("Are you sure you want to delete <b>%s</b>?" % selection.title())
            remove_check = QtWidgets.QMessageBox.question(self, "Confirm", msg,
                                                          QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
                                                          QtWidgets.QMessageBox.No)

            if remove_check == QtWidgets.QMessageBox.Yes:
                logger.info("Removing Item.")

                # Open Database and check for shows
                with open(show_database, "r") as f:
                    shows = json.load(f)

                for x in shows:
                    if x['name'].lower() in selection.lower():
                        shows.remove(x)

                with open(show_database, "w") as f:
                    json.dump(shows, f, indent=2)

                self.update_showtree()

            if remove_check == QtWidgets.QMessageBox.No:
                logger.info("Okay, I'll pretend that never happened.")

    class ScanShows(QtCore.QObject):

        update_progress = QtCore.pyqtSignal(int)
        update_available_tree = QtCore.pyqtSignal(str)

        def main(self):

            global download_list

            # Open database and check for shows
            with open(show_database, "r") as f:
                shows = json.load(f)

            show_list_length = len(shows)

            files = os.listdir(torrent_dir)
            current_id = 0
            download_list = {}  # Clear Download List
            self.update_progress.emit(0)

            for a in shows:
                parsed_shows_list = run_scan(a)
                ignore = 0

                for title, link, seeders, size in parsed_shows_list:

                    match = 0
                    # logger.debug([title, link])

                    # Filter List
                    for flag in ignore_flags:
                        if flag.lower() in title.lower():
                            ignore = 1

                    if ignore == 0:
                        if str(a['name']) in title:

                            # Check for existing torrent files, skip if existing, then Download latest
                            for i in files:
                                if (title + ".torrent") == i or (title + ".torrent.added") == i:
                                    match = 1
                                else:
                                    continue

                            if match == 0:

                                logger.info("Found an episode for %s!" % title)
                                self.update_available_tree.emit(title)
                                download_list.update({title: link})

                current_id += 1
                progress = (current_id / show_list_length) * 100
                self.update_progress.emit(progress)
                logger.debug("Progress: %s" % progress)

    if __name__ == '__main__':
        app = QtWidgets.QApplication(sys.argv)
        window = NyaaDownloader()
        window.show()
        sys.exit(app.exec_())

# -----------------------
# NAS MODE --------------

else:

    # http://download.synology.com/download/Document/DeveloperGuide/Synology_Download_Station_Web_API.pdf
    # https://github.com/mb243/SynoDL/blob/master/synodl.sh

    logger.warning("Running in NAS Mode.")

    class NyaaDownloaderNas:

        def __init__(self):

            global download_list
            download_list = []

            # Start the scan
            self.nas_scanshows()
            logger.info("Scan Complete!")

            if len(download_list) > 0:

                self.nas_download()

            else:
                logger.info("No new episodes found")

        def nas_scanshows(self):

            global download_list

            # Open database and check for shows
            with open(show_database, "r") as f:
                shows = json.load(f)

            show_list_length = len(shows)

            files = os.listdir(torrent_dir)
            current_id = 0
            download_list = {}  # Clear Download List

            for a in shows:
                parsed_shows_list = run_scan(a)
                ignore = 0

                for title, link, seeders, size in parsed_shows_list:
                    match = 0

                    # Filter List
                    for flag in ignore_flags:
                        if flag in title:
                            ignore = 1
                            logger.debug('Ignoring %s!' % title)

                    if ignore == 0:
                        if str(a['name']) in title:

                            # Check for existing torrent files, skip if existing, then Download latest
                            for i in files:
                                if (title + ".torrent") == i or (title + ".torrent.added") == i:
                                    match = 1
                                else:
                                    continue

                            if match == 0:
                                logger.info("Found an episode for %s!" % title)
                                download_list.update({title: link})

                current_id += 1
                progress = (current_id / show_list_length) * 100
                logger.debug("Progress: %s" % progress)

        @staticmethod
        def nas_download():

            # Download Torrent Files
            for title in download_list:
                torrent_file = os.path.join(torrent_dir, title + ".torrent")
                urllib.request.urlretrieve(download_list[title], torrent_file)
                logger.info("Downloading: %s" % title)

    # Run the Program
    NyaaDownloaderNas()

    # print("\n\n")
    # base_directory_nas = "/volume1/Media/.temp/transmission"
    # plex_directory = "/volume1/Media/Anime"
    # download_dir = os.path.join(base_directory_nas, "completed")
    # import plex_sync
    # plex_sync.run_sync(plex_directory, download_dir)

