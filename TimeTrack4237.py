import os
import sys
import json

from PyQt5 import QtWidgets as qtw

from MainWindow import MainWindow


CONFIG_FILENAME = 'config.json'


def get_database_filename() -> tuple:
    # Check if the config file exists.
    if not os.path.isfile(CONFIG_FILENAME):
        return False, 'Google config file does not exist.', {}

    # Open the files if it exists.
    with open(CONFIG_FILENAME, 'r') as fh:
        try:
            # Read the json string from the file into the config dictionary.
            config = json.load(fh)
            # Store the google config dictionary
            database_config = config['database config']
            return True, '', database_config['filename']
        except Exception as e:
            return False, 'Google config file is unreadable.', {}


def main() -> None:
    """
    This is the main method that starts the program.
    :return: None
    """
    success, message, filename = get_database_filename()

    if success and filename:
        app = qtw.QApplication(sys.argv)
        mw = MainWindow(filename)
        sys.exit(app.exec_())
    else:
        app = qtw.QApplication(sys.argv)
        message_box = qtw.QMessageBox()
        message_box.setIcon(qtw.QMessageBox.Critical)
        message_box.setWindowTitle('Config File Error')
        message_box.setText('The "config.json" file does not contain a database name.')
        message_box.setStandardButtons(qtw.QMessageBox.Ok)
        return_value = message_box.exec_()
        sys.exit(0)


if __name__ == '__main__':
    main()
