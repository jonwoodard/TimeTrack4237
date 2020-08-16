import os
import sys
import logging
import logging.config
import json
from PyQt5 import QtWidgets as qtw
import resources_rc

from MainWindow import MainWindow
from Console import Console

DATABASE_FILENAME = 'files/timetrack.db'
LOGGER_FILENAME = 'files/errorlogger.log'
LOG_CONFIG_FILENAME = 'files/config.json'
logger = logging.getLogger('TimeTrack')


def logging_setup():
    """This function is used to set up logging of errors and debugging information."""

    # This is the default logging configuration. It is used later if the configuration files is missing or corrupt.
    logging_config = {
        'version': 1,
        'loggers': {
            'TimeTrack': {
                'level': 'DEBUG',
                'handlers': ['console_handler', 'file_handler']
            }
        },
        'handlers': {
            'console_handler': {
                'level': 'DEBUG',
                'formatter': 'info',
                'class': 'logging.StreamHandler'
            },
            'file_handler': {
                'level': 'DEBUG',
                'formatter': 'error',
                'class': 'logging.FileHandler',
                'filename': LOGGER_FILENAME
            }
        },
        'formatters': {
            'info': {
                'format': '%(asctime)s %(levelname)4.4s >> line %(lineno)3s | %(module)s.%(funcName)s %(msg)s',
                'datefmt': '%Y-%m-%d %H:%M:%S'
            },
            'error': {
                'format': '%(asctime)s %(levelname)4.4s >> line %(lineno)3s | %(module)s.%(funcName)s %(msg)s',
                'datefmt': '%Y-%m-%d %H:%M:%S'
            }
        }
    }

    create_file = False
    # Check if the logging configuration files exists.
    if os.path.isfile(LOG_CONFIG_FILENAME):

        # Open the files if it exists.
        with open(LOG_CONFIG_FILENAME, 'r') as fh:
            try:
                # Read the json string from the files into the logging_config dictionary.
                logging_config = json.load(fh)
            except:
                # If there is an error reading from the files, then the files will be recreated below.
                create_file = True
    else:
        # If the logging configuration files does not exist, then the files will be created below.
        create_file = True

    # If the files does not exist or the files is corrupt, then recreate the files.
    if create_file:
        with open(LOG_CONFIG_FILENAME, 'w+') as fh:
            json.dump(logging_config, fh, indent=4)

    return logging_config


def main():
    """This is the main function that starts the program."""

    # Set up the logging of errors and debugging information
    logging_config = logging_setup()
    logging.config.dictConfig(logging_config)

    # Main menu to select the interface
    print('Select User Interface')
    print('1. Console UI')
    print('2. Graphical UI')
    choice = input('Choice? ')

    if choice == '1':
        m = Console(DATABASE_FILENAME)
        m.main_menu()
    else:
        app = qtw.QApplication(sys.argv)
        mw = MainWindow(DATABASE_FILENAME)
        sys.exit(app.exec_())


if __name__ == '__main__':
    main()
