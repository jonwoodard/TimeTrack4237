import os
import sys
import json

from PyQt5 import QtWidgets as qtw

from GoogleSheetManager import GoogleSheetManager
from DatabaseManager import DatabaseManager
from MainWindow import MainWindow


# The CONFIG_FILENAME is also defined in GoogleSheetManager.py
CONFIG_FILENAME = 'config.json'
THIS_DIRECTORY = os.path.dirname(os.path.realpath(__file__))


def get_config_file() -> tuple:
    # Check if the config file exists.
    config_file = os.path.join(THIS_DIRECTORY, CONFIG_FILENAME)

    if not os.path.isfile(config_file):
        return False, 'The config file does not exist.', ''
    else:
        return True, '', config_file


def get_database_file(config_file: str) -> tuple:
    # Open the config file and read it.
    with open(config_file, 'r') as fh:
        try:
            # Read the json string from the file into the config dictionary.
            config = json.load(fh)

            # Store the database config dictionary
            database_config = config['database config']

            folder, file = os.path.split(database_config['filename'])
            db_file = os.path.join(THIS_DIRECTORY, folder, file)
            return True, '', db_file
        except Exception as e:
            return False, 'Google config file is unreadable.', ''


def main() -> None:
    """
    This is the main method that starts the program.
    :return: None
    """

    # Check if the program was started with any options
    if len(sys.argv) > 1:
        if sys.argv[1] == '--upload':

            success, message, config_file = get_config_file()
            if success:
                success, message, db_file = get_database_file(config_file)
                if success:
                    gsm = GoogleSheetManager(db_file)
                    gsm.upload_data()
                    sys.exit(0)

        elif sys.argv[1] == '--logout':

            success, message, config_file = get_config_file()
            if not success:
                sys.exit(message)

            success, message, db_file = get_database_file(config_file)
            if not success:
                sys.exit(message)

            dbm = DatabaseManager(db_file)
            success, message = dbm.logout_all()
            if not success:
                sys.exit(message)

            sys.exit(0)

    else:

        app = qtw.QApplication(sys.argv)

        success, message, config_file = get_config_file()

        if success:
            success, message, db_file = get_database_file(config_file)

            if success:
                mw = MainWindow(db_file)
                sys.exit(app.exec_())

            else:
                message_box = qtw.QMessageBox()
                message_box.setIcon(qtw.QMessageBox.Critical)
                message_box.setWindowTitle('Config File Error')
                message_box.setText('The "config.json" file does not contain a "database filename".')
                message_box.setStandardButtons(qtw.QMessageBox.Ok)
                return_value = message_box.exec_()
                sys.exit(0)

        else:
            message_box = qtw.QMessageBox()
            message_box.setIcon(qtw.QMessageBox.Critical)
            message_box.setWindowTitle('Config File Error')
            message_box.setText('The "config.json" file does not exist.')
            message_box.setStandardButtons(qtw.QMessageBox.Ok)
            return_value = message_box.exec_()
            sys.exit(0)


if __name__ == '__main__':
    main()
