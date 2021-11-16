
import json
import os
import sys

from PyQt5 import QtWidgets, uic, QtCore, QtGui

from lumacode.nyaa import config, nyaa_downloader_functions
from lumacode import luma_log

ui_path = os.path.dirname(__file__)
ui_file = 'nyaa.ui'
Ui_MainWindow, QtBaseClass = uic.loadUiType(os.path.join(ui_path, ui_file), resource_suffix='')
logger = luma_log.main(__file__)


class ScanShows(QtCore.QObject):

    """
    Worker Thread for Scanning Shows

    """

    update_progress = QtCore.pyqtSignal(int)
    update_available_tree = QtCore.pyqtSignal(str)
    update_download_list = QtCore.pyqtSignal(dict)

    def main(self):

        # Open database and check for shows
        with open(config.show_database, "r") as f:
            shows = json.load(f)

        show_list_length = len(shows)

        print('checking %s for torrents.' % config.added_dir)
        current_id = 0
        download_list = {}  # Clear Download List
        self.update_progress.emit(0)

        for show in shows:
            parsed_shows_list, filtered_list = nyaa_downloader_functions.check_for_episodes(
                show['subgroup'],
                show['name'],
                show['fullhd']
            )

            for title, link in parsed_shows_list:

                if str(show['name']).lower() in title.lower():
                    logger.info("Found an episode for %s!" % title)
                    self.update_available_tree.emit(title)
                    download_list.update({title: link})

            for title in filtered_list:
                f = [x for x in config.filter_flags if x in title]
                logger.debug('omitting %s due to filter: %s' % (title, ''.join(f)))

            current_id += 1
            progress = (current_id / show_list_length) * 100

            if progress != 100:
                self.update_progress.emit(progress)
                logger.debug("Progress: %s" % progress)

        if len(download_list) > 0:
            self.update_download_list.emit(download_list)

        # Complete
        self.update_progress.emit(100)


# Define Window Class
class NyaaDownloader(QtWidgets.QMainWindow, Ui_MainWindow):

    def __init__(self):

        self.shows = []

        # Initialize UI
        QtWidgets.QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)
        self.download_list = {}

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
        self.show_tree.doubleClicked.connect(self.get_selected)

        # Setup Scan Thread
        self.scan_shows = ScanShows()
        self.thread1 = QtCore.QThread(self)
        self.scan_shows.update_progress.connect(self.update_progress)
        self.scan_shows.update_available_tree.connect(self.update_available_tree)
        self.scan_shows.update_download_list.connect(self.update_download_list)
        self.scan_shows.moveToThread(self.thread1)
        self.thread1.started.connect(self.scan_shows.main)

    def start_scan(self):
        self.download_list = {}
        self.thread1.start()

    def update_showtree(self):
        self.show_tree.clear()

        with open(config.show_database, "r") as f:
            self.shows = json.load(f)

        current_id = 1
        for show in self.shows:
            qt_item = QtWidgets.QTreeWidgetItem(self.show_tree)
            qt_item.setText(0, str(current_id))
            qt_item.setText(1, str(show['fullhd']))
            qt_item.setText(2, str(show['subgroup']))
            qt_item.setText(3, str(show['name']))
            current_id += 1

    @QtCore.pyqtSlot(str)
    def update_available_tree(self, title):
        qt_item = QtWidgets.QTreeWidgetItem(self.available_tree)
        qt_item.setText(0, str(title))

    @QtCore.pyqtSlot(dict)
    def update_download_list(self, download_list):
        self.download_list = download_list

    @QtCore.pyqtSlot(int)
    def update_progress(self, progress):

        # Progress Update
        if progress == 0:
            self.download_button.setEnabled(0)
            self.download_button.setStyleSheet('')
            self.available_tree.clear()  # We have just started scan, clean up the list.
            self.scan_progress.show()

        # Complete Signal
        if progress == 100:
            self.scan_progress.setValue(progress)
            logger.info("Scan Complete!")
            self.thread1.exit()  # Scan is complete. exit scanning thread.

            # New Episodes
            if len(self.download_list) > 0:
                self.download_button.setEnabled(1)
                self.download_button.setStyleSheet('background-color: #382; color: #fff;')

            # No Episodes
            else:
                self.download_button.setEnabled(0)
                qt_item = QtWidgets.QTreeWidgetItem(self.available_tree)
                qt_item.setText(0, str("No new episodes found..."))
                logger.info("No new episodes found")

        self.scan_progress.setValue(progress)

    def get_selected(self):

        # Get Selected Row
        selected_show = None
        indexes = self.show_tree.selectionModel().selectedRows(3)
        for index in sorted(indexes):
            selected_show = index.data()

        if selected_show:
            self.open_myanimelist(selected_show)

    def open_myanimelist(self, show):

        import subprocess

        url = 'https://myanimelist.net/anime.php?q=%s&cat=anime' % show
        if "windows" in config.platform_os.lower():
            cmd = ["C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe", url]
            subprocess.call(cmd)

        print(show)

    def download(self):

        nyaa_downloader_functions.download_torrents(self.download_list)

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
        dlg.setTextValue("SubsPlease, ")
        dlg.resize(500, 100)
        ok = dlg.exec_()
        value = dlg.textValue()

        if ok and len(value) > 1:

            # Open Database and check for shows
            with open(config.show_database, "r") as f:
                self.shows = json.load(f)

            try:
                value = value.split(", ")
                data_formatted = {'name': value[1], 'subgroup': value[0], 'fullhd': 'yes'}
                self.shows.append(data_formatted)

                if len(value[0]) > 1 and len(value[1]) > 1:

                    with open(config.show_database, "w") as f:
                        json.dump(self.shows, f, indent=2)

                    sanitized_path = value[1].strip()
                    show_path = os.path.join(config.plex_directory, sanitized_path)
                    logger.info("Added new show: " + value[1])
                    logger.info("Attempting to make directory in Plex: " + show_path)

                    try:
                        os.mkdir(show_path)

                    except Exception as e:
                        logger.error(e)

                    self.update_showtree()

                else:
                    logger.error("You didn't really put anything in did you...\n")

            except IndexError:

                logger.error("Error: Using wrong formatting!\n")

    def remove(self):

        # Get selected item
        selection = self.show_tree.currentItem().data(3, 0)
        logger.info("Sel ID: " + str(selection))

        with open(config.show_database, "r") as f:
            self.shows = json.load(f)

        msg = ("Are you sure you want to delete <b>%s</b>?" % selection.title())
        remove_check = QtWidgets.QMessageBox.question(self, "Confirm", msg,
                                                      QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
                                                      QtWidgets.QMessageBox.No)

        if remove_check == QtWidgets.QMessageBox.Yes:
            logger.info("Removing Item.")

            # Open Database and check for shows
            with open(config.show_database, "r") as f:
                self.shows = json.load(f)

            for x in self.shows:
                if x['name'].lower() in selection.lower():
                    self.shows.remove(x)

            with open(config.show_database, "w") as f:
                json.dump(self.shows, f, indent=2)

            self.update_showtree()

        if remove_check == QtWidgets.QMessageBox.No:
            logger.info("Okay, I'll pretend that never happened.")


def main():

    app = QtWidgets.QApplication(sys.argv)
    window = NyaaDownloader()
    window.show()

    # https://gist.github.com/QuantumCD/6245215
    app.setStyle(QtWidgets.QStyleFactory.create("Fusion"))
    palette = QtGui.QPalette()
    palette.setColor(QtGui.QPalette.Window, QtGui.QColor(53, 53, 53))
    palette.setColor(QtGui.QPalette.WindowText, QtCore.Qt.white)
    palette.setColor(QtGui.QPalette.Base, QtGui.QColor(25, 25, 25))
    palette.setColor(QtGui.QPalette.AlternateBase, QtGui.QColor(53, 53, 53))
    palette.setColor(QtGui.QPalette.ToolTipBase, QtCore.Qt.white)
    palette.setColor(QtGui.QPalette.ToolTipText, QtCore.Qt.white)
    palette.setColor(QtGui.QPalette.Text, QtCore.Qt.white)
    palette.setColor(QtGui.QPalette.Button, QtGui.QColor(53, 53, 53))
    palette.setColor(QtGui.QPalette.ButtonText, QtCore.Qt.white)
    palette.setColor(QtGui.QPalette.BrightText, QtCore.Qt.red)
    palette.setColor(QtGui.QPalette.Link, QtGui.QColor(42, 130, 218))

    palette.setColor(QtGui.QPalette.Highlight, QtGui.QColor(42, 130, 218))
    palette.setColor(QtGui.QPalette.HighlightedText, QtCore.Qt.black)
    palette.setColor(QtGui.QPalette.Disabled, QtGui.QPalette.ButtonText, QtCore.Qt.gray)
    palette.setColor(QtGui.QPalette.Disabled, QtGui.QPalette.WindowText, QtCore.Qt.gray)
    palette.setColor(QtGui.QPalette.Disabled, QtGui.QPalette.Text, QtCore.Qt.gray)
    palette.setColor(QtGui.QPalette.Disabled, QtGui.QPalette.Light, QtCore.Qt.darkGray)

    app.setPalette(palette)
    app.setStyleSheet("QToolTip { color: #ffffff; background-color: #2a82da; border: 1px solid white; }")

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
