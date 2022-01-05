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
    """The Main Window contains a title, a message, an input box, and the 'Checked In' list."""

    def __init__(self, db_filename: str):
        super(MainWindow, self).__init__()
        self.setupUi(self)
        self.setWindowModality(qtc.Qt.ApplicationModal)  # block input to all other windows
        self.setWindowFlag(qtc.Qt.Dialog)  # dialog box without min or max buttons
        self.setWindowFlag(qtc.Qt.FramelessWindowHint)  # borderless window that cannot be resized

        self.__db_filename = db_filename
        self.__db_manager = DatabaseManager(self.__db_filename)

        self.__timer = qtc.QTimer()       # a timer to display messages for a designated amount of time
        self.__timer.setSingleShot(True)

        # Set up the model-view structure for the 'Checked In' list.
        # As the data in the model changes, the view is updated automatically.
        # The QStringListModel is the easiest to implement since it does not require a customized model.
        checked_in_list = self.get_checked_in_list()
        self.__checked_in_model = qtc.QStringListModel(checked_in_list)
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

        # Use the timer to clear the message. The self.refresh_window() method will start the timer.
        # The static method qtc.QTimer.singleShot() will perform a similar operation, however
        #   if two students check in within the allotted time (3 seconds in this case)
        #   then the first message will be cut short (as it should be) but
        #   the second message will only display for the remaining time from the first message.
        self.__timer.timeout.connect(self.message.clear)

        #if platform.system() == 'Windows':
        #    self.show()
        #else:
        self.showFullScreen()

    @qtc.pyqtSlot(str)
    def barcode_scanned(self, barcode: str) -> None:
        """
        This slot is called when a barcode is scanned.
        It displays either (1) the Check In/Out window for Students, (2) the PIN dialog box for Admin,
        or (3) a message for an Invalid barcode.

        :param barcode: the barcode that was scanned
        :return: None
        """
        logger.debug(f'({barcode}) >> Started')

        success, message, barcode_type = self.__db_manager.check_barcode(barcode)
        # The "barcode_type" is either a Student, Admin, or Invalid.

        if barcode_type == 'Student':
            # Display the Check In/Out window.
            in_out_window = InOutWindow(self, self.__db_filename, barcode)

            # Refresh the Main window when the Check In/Out window closes.
            # The "window_closed" signal emits a "message" to display on the Main window for 3 seconds.
            in_out_window.window_closed.connect(lambda message: self.refresh_window(message, 3))

        elif barcode_type == 'Admin':
            # Display a Number Pad dialog box for the user to enter their Admin PIN.
            admin_pin_dialog_box = NumberPadDialogBox(self)
            admin_pin_dialog_box.title.setText('Enter PIN')
            admin_pin_dialog_box.entry.setEchoMode(qtw.QLineEdit.Password)

            # When the Number Pad dialog box closes, decide whether to display the Admin window or an Error message.
            # The "window_closed" signal emits two strings:
            #   (1) the button clicked to close the window (OK or Cancel) and (2) the pin entered.
            admin_pin_dialog_box.window_closed.connect(
                lambda pin: self.admin_pin_dialog_box_closed(barcode, pin))

        elif barcode_type == 'Invalid':
            # Display an error message on the Main window for an Invalid barcode.
            self.refresh_window('Invalid Barcode. Try Again.', 3)
            logger.critical('Invalid Barcode')

    @qtc.pyqtSlot(str, str)
    def admin_pin_dialog_box_closed(self, barcode: str, pin: str) -> None:
        """
        This slot is called when the Number Pad dialog box is closed to get an Admin PIN.
        It checks the Admin PIN to decide whether to display the Admin window or an error message on the Main window.

        :param barcode: the barcode scanned
        :param pin: the Admin PIN entered
        :return: None
        """
        logger.debug(f'({barcode}, {pin} >> Started')

        if pin:

            # Check if the Admin PIN is correct.
            success, message, correct_pin = self.__db_manager.check_pin(barcode, pin)
            if correct_pin:
                # Display the Admin window since the Admin PIN is correct.
                admin_window = AdminWindow(self, self.__db_filename)
                admin_window.window_closed.connect(lambda: self.refresh_window('', 0))
            else:
                # Display an error message on the Main window since the PIN was incorrect.
                self.refresh_window('Incorrect PIN.', 3)

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
        logger.debug(f'({message}, {seconds}) >> Started')

        # Clear the barcode that was scanned.
        self.barcode.clear()

        # Update the 'Checked In' list.
        checked_in_list = self.get_checked_in_list()
        self.__checked_in_model.setStringList(checked_in_list)

        # Display the "message" for X seconds if one was passed, otherwise clear the message
        if message:
            self.message.setText(message)

            # Start the timer. Once the timer expires, the timeout signal is triggered.
            self.__timer.start(int(1000 * seconds))
        else:
            self.message.clear()

    def get_checked_in_list(self) -> list:
        """
        This method returns the 'Checked In' list to display on the Main window.
        The QStringListModel requires a list of strings, so this method formats the data for that.

        :return: a list of strings: ['<id>  lastname, firstname', ... ]
        """
        logger.debug(' >> Started')

        format_data = list()

        # "data" is a list of tuples: [('id', 'firstname', 'lastname'), ... ]
        success, message, data = self.__db_manager.get_checked_in_list()
        if success:
            # Concatenate each tuple of strings into a single formatted string
            # "format_data" is a list of strings: ['<id>  lastname, firstname', ... ]
            for tup in data:
                format_data.append('<' + tup[0] + '>  ' + tup[2] + ', ' + tup[1])

        return format_data
