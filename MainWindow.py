import gc
import platform
import csv
import os

from PyQt5 import QtWidgets as qtw
from PyQt5 import QtCore as qtc
from gui.Ui_MainWindow import Ui_MainWindow
from InOutWindow import InOutWindow
from AdminWindow import AdminWindow
from DatabaseManager import DatabaseManager
from NumberPadDialogBox import NumberPadDialogBox
from GoogleSheetManager import GoogleSheetManager


class MainWindow(qtw.QWidget, Ui_MainWindow):
    """The Main Window contains a title, a message, an input box, and the 'Checked In' list."""

    def __init__(self, filename: str):
        super().__init__()
        self.setupUi(self)
        self.setWindowModality(qtc.Qt.ApplicationModal)  # block input to all other windows
        self.setWindowFlag(qtc.Qt.Window)  # dialog box without min or max buttons
        self.setWindowFlag(qtc.Qt.FramelessWindowHint)  # borderless window that cannot be resized

        self.__filename = filename
        self.__barcode = ''
        self.__db_manager = DatabaseManager(self.__filename)
        self.__in_out_window = InOutWindow(self, self.__db_manager)
        self.__admin_window = AdminWindow(self, self.__db_manager)
        self.__admin_pin_dialog_box = NumberPadDialogBox(self)

        # self.__admin_pin_dialog_box.title.setText('Enter PIN')
        self.__admin_pin_dialog_box.entry.setEchoMode(qtw.QLineEdit.Password)

        self.__timer = qtc.QTimer()       # a timer to display messages for a designated amount of time
        self.__timer.setSingleShot(True)

        # Set up the model-view structure for the 'Checked In' list.
        # As the data in the model changes, the view is updated automatically.
        # The QStringListModel is the easiest to implement since it does not require a customized model.
        self.__checked_in_list = self.get_checked_in_list()
        self.__checked_in_model = qtc.QStringListModel(self.__checked_in_list)
        self.checkedInList.setModel(self.__checked_in_model)

        self.checkedInList.setFocusPolicy(qtc.Qt.NoFocus)
        self.checkedInList.setVerticalScrollBarPolicy(qtc.Qt.ScrollBarAlwaysOn)
        self.checkedInList.setHorizontalScrollBarPolicy(qtc.Qt.ScrollBarAlwaysOff)
        self.checkedInList.setAutoScroll(False)
        self.checkedInList.setAutoScrollMargin(400)
        self.checkedInList.setEditTriggers(qtw.QAbstractItemView.NoEditTriggers)
        self.checkedInList.setSelectionMode(qtw.QAbstractItemView.NoSelection)

        self.barcode.setEchoMode(qtw.QLineEdit.Password)  # hide the barcode number that was scanned, like a password

        # When a barcode is scanned, the 'returnPressed' signal emits which calls the 'barcode_scanned' slot.
        self.barcode.returnPressed.connect(lambda: self.barcode_scanned(self.barcode.text()))

        # Refresh the Main window when the Check In/Out window closes.
        # The "window_closed" signal emits a "message" to display on the Main window for 3 seconds.
        self.__in_out_window.window_closed.connect(lambda message: self.refresh_window(message, 3))

        # When the Number Pad dialog box closes, decide whether to display the Admin window or an Error message.
        # The "window_closed" signal emits two strings:
        #   (1) the button clicked to close the window (OK or Cancel) and (2) the pin entered.
        self.__admin_pin_dialog_box.window_closed.connect(
            lambda pin: self.admin_pin_dialog_box_closed(pin))

        # Display the Admin window when the Admin PIN is correct.
        self.__admin_window.window_closed.connect(lambda: self.refresh_window('', 0))

        # Use the timer to clear the message. The self.refresh_window() method will start the timer.
        # The static method qtc.QTimer.singleShot() will perform a similar operation, however
        #   if two students check in within the allotted time (3 seconds in this case)
        #   then the first message will be cut short (as it should be) but
        #   the second message will only display for the remaining time from the first message.
        self.__timer.timeout.connect(self.message.clear)

        # Use an event timer to schedule the auto logout and upload data feature
        self.__event_timer = qtc.QTimer()
        self.__event_timer.setSingleShot(True)
        self.__event_timer.timeout.connect(lambda: self.run_task())
        self.set_event_timer()

        if platform.system() == 'Windows':
            self.show()
        else:
            self.showFullScreen()

        self.check_database()  # check if the database file exists after the main window displays

    def set_event_timer(self) -> None:
        # Get the current date and time.
        current_datetime = qtc.QDateTime().toLocalTime().currentDateTime()

        # Set the date and time for the next event to today at 1am.
        event_datetime = qtc.QDateTime(current_datetime.date(), qtc.QTime(1, 0, 0))

        # Check if the event date and time has already passed for today.
        # Add a day to the event date if the event time has already passed today.
        # NOTE: this is mostly for the initial startup of the program, to get the first event set correctly.
        if current_datetime > event_datetime:
            event_datetime = event_datetime.addDays(1)

        # Start the event timer
        self.__event_timer.start(current_datetime.msecsTo(event_datetime))

    @qtc.pyqtSlot()
    def run_task(self) -> None:
        """
        This slot is called when the event_timer expires.
        It will logout all users that are still checked in and upload the data to a Google Sheet.
        :return: None
        """

        # Logout all users that are still checked in.
        success1, message1 = self.__db_manager.logout_all()
        self.refresh_window()

        # Upload the data to the Google Sheet.
        gsm = GoogleSheetManager(self.__db_manager)
        success2, _, message2 = gsm.upload_data()

        # Reset the event timer to run this task again tomorrow.
        self.set_event_timer()

        gc.enable()
        gc.collect()

    def check_database(self) -> None:
        # Check if the database file exists.
        if not os.path.isfile(self.__filename):
            text = 'The database file "' + self.__filename + '" is missing.'
            result = self.__display('Database File Missing', text,
                                    'Would you like to create it now?', '', qtw.QMessageBox.Yes | qtw.QMessageBox.No)

            if result == qtw.QMessageBox.Yes:
                # Create the database file, along with tables, indexes, and triggers.
                success, message, counter, total = self.__db_manager.create_database()

                if success:
                    # Ask if the user wants to import data.
                    text = 'The database has been created successfully, but contains no student records.'
                    result = self.__display('Import Student Records', text,
                                            'Would you like to import student records from a csv file?',
                                            '', qtw.QMessageBox.Yes | qtw.QMessageBox.No)

                    if result == qtw.QMessageBox.Yes:
                        self.__import_records('student')

                        result = self.__display('Import Activity Records', 'The database contains no activity records.',
                                                'Would you like to import SAMPLE activity records from a csv file?',
                                                '', qtw.QMessageBox.Yes | qtw.QMessageBox.No)
                        if result == qtw.QMessageBox.Yes:
                            self.__import_records('activity')

                else:
                    text = 'Only created ' + str(counter) + ' out of ' + str(total) + ' database objects.'
                    self.__display('Database Error', text)

            else:
                self.__display('Database Error', 'This application requires a database file.')

    def __import_records(self, table: str) -> None:
        # Let the user select the file to import.
        this_directory = os.path.dirname(os.path.realpath(__file__))
        csv_filename, _ = qtw.QFileDialog.getOpenFileName(self, 'Open a file', this_directory, 'csv (*.csv)')
        _, file_extension = os.path.splitext(csv_filename)
        if file_extension == '.csv':

            # The with ... as statement will open the file and close the file at the end.
            with open(csv_filename, 'r') as fh:
                csv_reader = csv.reader(fh)
                counter = 0
                for record in csv_reader:
                    self.__db_manager.new_record(table, tuple(record))
                    counter += 1

                self.__display('Import Success', 'Imported ' + str(counter) + ' ' + table + ' records.')

    @qtc.pyqtSlot(str)
    def barcode_scanned(self, barcode: str) -> None:
        """
        This slot is called when a barcode is scanned.
        It displays either (1) the Check In/Out window for Students, (2) the PIN dialog box for Admin,
        or (3) a message for an Invalid barcode.

        :param barcode: the barcode that was scanned
        :return: None
        """

        self.__barcode = barcode
        success, message, barcode_type = self.__db_manager.check_barcode(self.__barcode)
        # The "barcode_type" is either a Student, Admin, or Invalid.

        if barcode_type == 'Student':
            # Display the Check In/Out window.
            self.__in_out_window.show_window(self.__barcode)

        elif barcode_type == 'Admin':
            # Display a Number Pad dialog box for the user to enter their Admin PIN.
            self.__admin_pin_dialog_box.show_window('Enter PIN')

        elif barcode_type == 'Invalid':
            # Display an error message on the Main window for an Invalid barcode.
            self.refresh_window('Invalid Barcode. Try Again.', 3)

        elif barcode_type == 'Error':
            # Display an error message on the Main window because of a Database error.
            self.refresh_window('Database Error. See Admin.', 3)

    @qtc.pyqtSlot(str)
    def admin_pin_dialog_box_closed(self, pin: str) -> None:
        """
        This slot is called when the Number Pad dialog box is closed to get an Admin PIN.
        It checks the Admin PIN to decide whether to display the Admin window or an error message on the Main window.

        :param barcode: the barcode scanned
        :param pin: the Admin PIN entered
        :return: None
        """

        if pin:

            # Check if the Admin PIN is correct.
            success, message, correct_pin = self.__db_manager.check_pin(self.__barcode, pin)
            if correct_pin:
                # Display the Admin window since the Admin PIN is correct.
                self.__admin_window.show_window(self.__checked_in_list)

            else:
                # Display an error message on the Main window since the PIN was incorrect.
                self.refresh_window('Incorrect PIN.', 3)

            pin = None

        else:  # if the 'Cancel' button was clicked (or any other reason)
            self.refresh_window()

    @qtc.pyqtSlot(str, float)
    def refresh_window(self, message: str = '', seconds: float = 0.0) -> None:
        """
        Refresh the data fields on the Main Window (barcode, checked in list, and message).
        :param message: the message to display at the bottom
        :param seconds: the duration of the message
        :return: None
        """

        # Clear the barcode that was scanned.
        self.barcode.clear()
        self.__barcode = ''

        # Update the 'Checked In' list.
        self.__checked_in_list = self.get_checked_in_list()
        self.__checked_in_model.setStringList(self.__checked_in_list)

        # Display the "message" for X seconds if one was passed, otherwise clear the message
        if message:
            self.message.setText(message)

            # Start the timer. Once the timer expires, the timeout signal is triggered.
            self.__timer.start(int(1000 * seconds))
        else:
            self.message.clear()

        # print(len(gc.get_referrers(self.__checked_in_list)))
        gc.enable()
        gc.collect()

    def get_checked_in_list(self) -> list:
        """
        This method returns the 'Checked In' list to display on the Main window.
        The QStringListModel requires a list of strings, so this method formats the data for that.

        :return: a list of strings: ['<id>  lastname, firstname', ... ]
        """

        format_data = list()

        # "data" is a list of tuples: [('id', 'firstname', 'lastname'), ... ]
        success, message, data = self.__db_manager.get_checked_in_list()
        if success:
            # Concatenate each tuple of strings into a single formatted string
            # "format_data" is a list of strings: ['<id>  lastname, firstname', ... ]
            for tup in data:
                # format_data.append('<' + tup[0] + '>  ' + tup[2] + ', ' + tup[1])
                format_data.append(tup[2] + ', ' + tup[1])

        return format_data

    def __display(self, title: str, text: str, informative_text: str = '', detailed_text: str = '',
                  buttons: qtw.QMessageBox.StandardButton = qtw.QMessageBox.Ok) -> int:
        message_box = qtw.QMessageBox(self)
        message_box.setIcon(qtw.QMessageBox.Information)

        message_box.setWindowTitle(title)
        message_box.setText(text)

        if informative_text:
            message_box.setInformativeText(informative_text)
        if detailed_text:
            message_box.setDetailedText(detailed_text)

        message_box.setStandardButtons(buttons)

        return_value = message_box.exec_()
        return return_value
