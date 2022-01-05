import os
import sys
import logging
import logging.config
import json
from PyQt5 import QtWidgets as qtw

from MainWindow import MainWindow
from Console import Console

DATABASE_FILENAME = 'files/timetrack.db'
LOGGER_FILENAME = 'files/errorlogger.log'
CONFIG_FILENAME = 'config.json'
logger = logging.getLogger('TimeTrack')


def config_file_setup() -> dict:
    # This is the default logging configuration. It is used later if the configuration files is missing or corrupt.
    config = {
        'logging config': {
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
        },
        'google config': {
            'service account': 'credentials/timetrack4237-1597581877356-3520afa3c807.json',
            'spreadsheet url': 'https://docs.google.com/spreadsheets/d/1VcbaNq8Cy8LKNns1tbURN2HoRnIKh1OU2jVC8qc1nDM',
            'worksheet name': '2020-2021'
        }
    }

    return config


def logging_setup() -> dict:
    """
    This method is used to set up logging of errors and debugging information.
    It grabs the data from the config file, if it exists. Otherwise it creates the config file.

    :return: dictionary of the logging configuration
    """

    config = config_file_setup()
    logging_config = config['logging config']

    create_file = False
    # Check if the logging configuration files exists.
    if os.path.isfile(CONFIG_FILENAME):

        # Open the files if it exists.
        with open(CONFIG_FILENAME, 'r') as fh:
            try:
                # Read the json string from the file into the logging_config dictionary.
                config = json.load(fh)
                logging_config = config['logging config']
            except:
                # If there is an error reading from the file, then the files will be recreated below.
                create_file = True
    else:
        # If the logging configuration files does not exist, then the files will be created below.
        create_file = True

    # If the files does not exist or the file is corrupt, then recreate the file.
    if create_file:
        with open(CONFIG_FILENAME, 'w+') as fh:
            json.dump(logging_config, fh, indent=4)

    return logging_config


def main() -> None:
    """
    This is the main method that starts the program.
    :return: None
    """

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
