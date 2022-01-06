from PyQt5 import QtWidgets as qtw
from PyQt5 import QtCore as qtc
from PyQt5 import QtGui as qtg

from gui.Ui_AdminWindow import Ui_AdminWindow
from DatabaseManager import DatabaseManager


class AdminWindow(qtw.QWidget, Ui_AdminWindow):
    """The Admin contains an Upload Data button, a Check Out ALL button, a Cancel button,
        and the Hours Logged table."""

    # Signal to indicate that the Check In/Out window was closed.
    window_closed = qtc.pyqtSignal(str)

    def __init__(self, parent: qtw.QWidget, db_filename: str, barcode: str):
        super().__init__(parent)
        self.setupUi(self)

        # Force the user to interact with this window
        self.setWindowModality(qtc.Qt.ApplicationModal)  # block input to all other windows
        self.setWindowFlag(qtc.Qt.Dialog)                # dialog box without min or max buttons
        self.setWindowFlag(qtc.Qt.FramelessWindowHint)   # borderless window that cannot be resized

        self.__db_manager = DatabaseManager(db_filename)
        self.__barcode = barcode

        # "data" is a 4-tuple: (firstname, lastname, status, total_hours)
        # success, message, data = self.__db_manager.get_student_data(self.__barcode)

        # Set the data to display in the Check In/Out window.
        self.adminName.setText("Sir Lance-A-Bot")
        # self.adminName.setText(data[0] + ' ' + data[1])

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

        self.checkOutAllButton.setToolTip('Check Out ALL students that are currently Checked In')
        self.uploadDataButton.setToolTip('Upload Data to Google Sheets')

        # Disable buttons if needed.
        if len(checked_in_list) == 0:
            self.disable_button(self.checkOutAllButton, 'No students currently Checked In')

        # # Signals to indicate which button was clicked.
        self.exitButton.clicked.connect(lambda: self.clicked('Exit'))
        self.uploadDataButton.clicked.connect(lambda: self.clicked('Upload Data'))
        self.checkOutAllButton.clicked.connect(lambda: self.clicked('Check Out ALL'))

        self.showFullScreen()

    @qtc.pyqtSlot(str)
    def clicked(self, button_name: str) -> None:
        """
        This slot is called when a button is clicked.

        :param button_name: the name of the button clicked
        :return: None, emits the "window_closed" signal and passes a message to display on the Main window
        """

        # Determine which button was clicked and set the message to be displayed.
        if button_name == 'Exit':
            self.window_closed.emit('Successful Exit.')
            self.close()
        elif button_name == 'Upload Data':
            self.__db_manager.upload_student_data_to_google_sheet()
            self.disable_button(self.uploadDataButton, 'Data already uploaded')
        elif button_name == 'Check Out ALL':
            # "data" is a list of tuples: [('id', 'firstname', 'lastname'), ... ]
            success, message, data = self.__db_manager.get_checked_in_list()
            for tup in data:
                self.__db_manager.checkout_student(tup[0])

            self.__checked_in_model.setStringList([])
            self.disable_button(self.checkOutAllButton, 'No students currently Checked In')

    def disable_button(self, button: qtw.QPushButton, tool_tip: str) -> None:
        """
        This method enables the correct buttons and sets the tool tips font.

        :param button: the button to disable
        :param tool_tip: the tool tip to display
        :return: None
        """

        if button:
            button.setEnabled(False)
            button.setToolTip(tool_tip)
            font = qtg.QFont()
            font.setBold(False)
            font.setPointSize(24)
            button.setFont(font)

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
                format_data.append('<' + tup[0] + '>  ' + tup[2] + ', ' + tup[1])

        return format_data
