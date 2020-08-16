import logging
from PyQt5 import QtWidgets as qtw
from PyQt5 import QtCore as qtc

from gui.Ui_MainWindow import Ui_MainWindow
from InOutWindow import InOutWindow
from AdminWindow import AdminWindow
from DatabaseManager import DatabaseManager
from NumberPadDialogBox import NumberPadDialogBox

logger = logging.getLogger('TimeTrack.MainWindow')


class MainWindow(qtw.QWidget, Ui_MainWindow):
    """The View (GUI) of the Main Window."""

    def __init__(self, db_filename: str):
        super(MainWindow, self).__init__()
        self.setupUi(self)
        self.__db_filename = db_filename

        self.setWindowModality(qtc.Qt.ApplicationModal)
        self.setWindowFlag(qtc.Qt.Dialog)
        self.setWindowFlag(qtc.Qt.FramelessWindowHint)

        self.__data_model = DataModel(self.__db_filename)

        self.__timer = qtc.QTimer()
        self.__timer.setSingleShot(True)

        # Set up the Model for the Checked In List
        checked_in_list = self.__data_model.get_checked_in_list()
        self.__checked_in_model = qtc.QStringListModel(checked_in_list)
        self.checkedInList.setModel(self.__checked_in_model)
        self.checkedInList.setFocusPolicy(qtc.Qt.NoFocus)
        self.checkedInList.setVerticalScrollBarPolicy(qtc.Qt.ScrollBarAlwaysOn)
        self.checkedInList.setHorizontalScrollBarPolicy(qtc.Qt.ScrollBarAlwaysOff)
        self.checkedInList.setAutoScroll(False)
        self.checkedInList.setAutoScrollMargin(400)
        self.checkedInList.setEditTriggers(qtw.QAbstractItemView.NoEditTriggers)
        self.checkedInList.setSelectionMode(qtw.QAbstractItemView.NoSelection)

        self.barcode.setEchoMode(qtw.QLineEdit.Password)

        # ***** SIGNALS ******
        # When a barcode is scanned, the 'barcode.returnPressed' signal emits which calls the 'check_barcode' slot.
        self.barcode.returnPressed.connect(lambda: self.__data_model.check_barcode(self.barcode.text()))

        # When a barcode is scanned and then checked, the 'barcode_checked' signal emits which calls the
        #   'barcode_scanned' slot.
        self.__data_model.barcode_checked.connect(self.barcode_scanned)

        # Use the timer to clear the message. The self.refresh_window() method will start the timer.
        # The static method qtc.QTimer.singleShot() will perform a similar operation, however
        #   if two students check in within 3 seconds then the first message will be cut short (as it should be) but
        #   the second message will only display for the remaining time from the first message.
        self.__timer.timeout.connect(self.message.clear)

        #if platform.system() == 'Windows':
        #    self.show()
        #else:
        self.showFullScreen()

    @qtc.pyqtSlot(str, str)
    def barcode_scanned(self, barcode: str, barcode_type: str):
        """Display the correct window once a barcode is scanned."""
        logger.debug(f'({barcode}, {barcode_type}) >> Started')

        # The barcode scanned is either a Student, Admin, or Invalid barcode.
        if barcode_type == 'Student':
            in_out_window_view = InOutWindow(self, self.__db_filename, barcode)
            in_out_window_view.window_closed.connect(lambda message: self.refresh_window(message, 3))

        elif barcode_type == 'Admin':
            # Ask the user to enter the Admin PIN for the barcode scanned.
            keypad_dialog_box = NumberPadDialogBox(self)
            keypad_dialog_box.title.setText('Enter PIN')
            keypad_dialog_box.entry.setEchoMode(qtw.QLineEdit.Password)
            keypad_dialog_box.window_closed.connect(lambda button_name, pin: self.admin_window(button_name, barcode, pin))

        elif barcode_type == 'Invalid':
            self.refresh_window('Invalid Barcode. Try Again.', 3)
            logger.critical('Invalid Barcode')

    @qtc.pyqtSlot(str, str, str)
    def admin_window(self, button_name: str, barcode: str, pin: str):
        """Open the admin window if the pin is a match for the barcode."""
        logger.debug(f'({button_name}, {barcode}, {pin} >> Started')

        if button_name == 'OK':
            success, message, valid = self.__data_model.check_admin_pin(barcode, pin)
            if valid:
                admin_window = AdminWindow(self, self.__db_filename)
                admin_window.window_closed.connect(lambda: self.refresh_window('', 0))
            else:
                self.refresh_window('Incorrect PIN.', 3)
        else:
            self.refresh_window()

    @qtc.pyqtSlot(str, float)
    def refresh_window(self, message: str = '', seconds: float = 0.0):
        """Refresh the data fields on the window (barcode, checked in list, and message)."""
        logger.debug(f'({message}, {seconds}) >> Started')

        # Clear the barcode
        self.barcode.clear()

        # Update the Checked In List
        checked_in_list = self.__data_model.get_checked_in_list()
        self.__checked_in_model.setStringList(checked_in_list)

        # Display the message for X seconds if one was passed, otherwise clear the message
        if message:
            self.message.setText(message)

            # Start the timer. Once the timer expires, the timeout signal is triggered.
            self.__timer.start(int(1000 * seconds))
        else:
            self.message.clear()


class DataModel(qtc.QObject):
    """The Model (data) of the Application, connecting to the database."""

    # Signal to indicate if the barcode scanned is a Student, Admin, or Invalid.
    barcode_checked = qtc.pyqtSignal(str, str)

    def __init__(self, db_filename: str):
        super().__init__()

        # The Database Manager is private to this class.
        self.__db_manager = DatabaseManager(db_filename)

    def get_checked_in_list(self):
        """This method will return the Check In List to display on the Main Window."""
        logger.debug(' >> Started')

        success, message, data = self.__db_manager.get_checked_in_list()
        return data

    def check_admin_pin(self, barcode: str, pin: str):
        """This method will check if an admin pin is correct."""
        logger.debug(' >> Started')

        return self.__db_manager.check_pin(barcode, pin)

    @qtc.pyqtSlot(str)
    def check_barcode(self, barcode: str):
        """This slot is called when a barcode is scanned. It emits one of two signals indicating the validity."""
        logger.debug(f'({barcode}) >> Started')

        success, message, barcode_type = self.__db_manager.check_barcode(barcode)
        self.barcode_checked.emit(barcode, barcode_type)

