import gc
import platform

from PyQt5 import QtWidgets as qtw
from PyQt5 import QtCore as qtc
from PyQt5 import QtGui as qtg

from gui.Ui_AdminWindow import Ui_AdminWindow
from DatabaseManager import DatabaseManager
from GoogleSheetManager import GoogleSheetManager


class AdminWindow(qtw.QWidget, Ui_AdminWindow):
    """The Admin contains an Upload Data button, a Check Out ALL button, a Cancel button,
        and the Hours Logged table."""

    # Signal to indicate that the Admin window was closed.
    window_closed = qtc.pyqtSignal(str)

    # def __init__(self, parent: qtw.QWidget, db_filename: str, barcode: str):
    def __init__(self, parent: qtw.QWidget, db_manager: DatabaseManager):
        super().__init__(parent)
        self.setupUi(self)

        # Force the user to interact with this window
        self.setWindowModality(qtc.Qt.ApplicationModal)  # block input to all other windows
        self.setWindowFlag(qtc.Qt.Dialog)                # dialog box without min or max buttons
        self.setWindowFlag(qtc.Qt.FramelessWindowHint)   # borderless window that cannot be resized

        self.__db_manager = db_manager
        self.__gsm = GoogleSheetManager(self.__db_manager)

        self.__checked_in_list = []
        self.__checked_in_model = qtc.QStringListModel(self.__checked_in_list)
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

        # Signals to indicate which button was clicked.
        self.exitButton.clicked.connect(lambda: self.clicked('Exit'))
        self.uploadDataButton.clicked.connect(lambda: self.clicked('Upload Data'))
        self.checkOutAllButton.clicked.connect(lambda: self.clicked('Check Out ALL'))

        self.hide()

    def __config_window(self):
        # "data" is a 4-tuple: (firstname, lastname, status, total_hours)
        # success, message, data = self.__db_manager.get_student_data(self.__barcode)

        # Set the data to display in the Admin window.
        self.adminName.setText("Sir Lance-A-Bot")
        # self.adminName.setText(data[0] + ' ' + data[1])

        # Set up the model-view structure for the 'Checked In' list.
        # As the data in the model changes, the view is updated automatically.
        # The QStringListModel is the easiest to implement since it does not require a customized model.
        self.__checked_in_model.setStringList(self.__checked_in_list)

        # Disable buttons if needed.
        if len(self.__checked_in_list) == 0:
            self.set_button_state(self.checkOutAllButton, 'No students currently Checked In', False)
        else:
            self.set_button_state(self.checkOutAllButton, 'Check Out ALL students that are currently Checked In', True)

        self.set_button_state(self.uploadDataButton, 'Upload Data to Google Sheets', True)

    def show_window(self, checked_in_list: list):
        self.__checked_in_list = checked_in_list
        self.__config_window()
        if platform.system() == 'Windows':
            self.show()
        else:
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
            self.hide()
            self.__clean_up()

        elif button_name == 'Upload Data':
            success, title, message = self.__gsm.upload_data()
            if success:
                text = 'The data was uploaded successfully to the Google Sheet.'
                self.__display('Upload Success', text)
            else:
                self.__display(title, message)

            self.set_button_state(self.uploadDataButton, 'Data already uploaded', False)

        elif button_name == 'Check Out ALL':
            # "data" is a list of tuples: [('id', 'firstname', 'lastname'), ... ]
            # NOTE: this is not the same format as self.__checked_in_list
            success, message, data = self.__db_manager.get_checked_in_list()
            for tup in data:
                self.__db_manager.checkout_student(tup[0])

            self.__checked_in_model.setStringList([])
            self.set_button_state(self.checkOutAllButton, 'No students currently Checked In', False)

    def set_button_state(self, button: qtw.QPushButton, tool_tip: str, is_enabled: bool) -> None:
        """
        This method enables the correct buttons and sets the tool tips font.

        :param button: the button to disable
        :param tool_tip: the tool tip to display
        :param is_enabled: is the button enabled
        :return: None
        """

        if button:
            button.setEnabled(is_enabled)
            button.setToolTip(tool_tip)

            font = qtg.QFont()
            font.setBold(is_enabled)
            if is_enabled:
                font.setPointSize(26)
            else:
                font.setPointSize(24)
            button.setFont(font)

    def __clean_up(self):
        gc.enable()
        self.__checked_in_list.clear()
        self.__checked_in_model.setStringList([])
        gc.collect()

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

