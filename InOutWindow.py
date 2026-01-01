import gc
import platform
from PyQt5 import QtWidgets as qtw
from PyQt5 import QtCore as qtc
from PyQt5 import QtGui as qtg
from gui.Ui_InOutWindow import Ui_InOutWindow
from DatabaseManager import DatabaseManager


class HoursTableModel(qtc.QAbstractTableModel):
    """The Model (data) for the Hours Table on the Check In/Out Window."""

    def __init__(self, hours_table_model: list, header: tuple):
        super().__init__()

        self.__data = hours_table_model
        self.__header = header

    def rowCount(self, parent: qtc.QModelIndex = qtc.QModelIndex()) -> int:
        """
        This *required* method overrides the abstract method in the parent class.
        It returns the number of rows in the table.

        :param parent: the parent of the widget
        :return: the number of rows in the table
        """

        return len(self.__data)

    def columnCount(self, parent: qtc.QModelIndex = qtc.QModelIndex()) -> int:
        """
        This *required* method overrides the abstract method in the parent class.
        It returns the number of columns in the table.

        :param parent: the parent of the widget
        :return: the number of columns in the table
        """

        if self.__data:
            return len(self.__data[0])
        else:
            return 0

    def data(self, index: qtc.QModelIndex, role: qtc.Qt.ItemDataRole = qtc.Qt.DisplayRole):
        """
        This *required* method overrides the abstract method in the parent class.
        It returns the data and formatting for the data.

        :param index: the row and column of the data being requested
        :param role: the purpose for this request of data (display, alignment, font, etc.)
        :return: the type returned varies depending on the role
        """

        row = index.row()
        column = index.column()

        # The role indicates the purpose for calling this method and also indicates the type of data to return.
        # There are more roles available if needed.
        if role == qtc.Qt.DisplayRole:
            if self.__data:
                return self.__data[row][column]
            else:
                return None

        elif role == qtc.Qt.TextAlignmentRole:
            if column == 0:
                return qtc.Qt.AlignLeft + qtc.Qt.AlignVCenter
            elif column == 1:
                return qtc.Qt.AlignHCenter + qtc.Qt.AlignVCenter
            elif column == 2:
                return qtc.Qt.AlignRight + qtc.Qt.AlignVCenter

        elif role == qtc.Qt.FontRole:
            font = qtg.QFont()
            font.setFamily("MS Shell Dlg 2")
            font.setPointSize(14)
            return font

        return None

    def headerData(self, section: int, orientation: qtc.Qt.Orientation, role: qtc.Qt.ItemDataRole = qtc.Qt.DisplayRole):
        """
        This method overrides the abstract method in the parent class.
        It returns the headers and formatting for the horizontal headers.

        :param section: the column number of the table, starting at 0
        :param orientation: either Vertical (for row) headers or Horizontal (for column) headers
        :param role: the purpose for this request of data (display, alignment, font, etc.)
        :return: the type returned varies depending on the role
        """

        # The orientation is used to indicate either horizontal or vertical headers.
        # This table is only using horizontal headers, so return immediately for vertical headers.
        if orientation != qtc.Qt.Horizontal:
            return None

        # The role indicates the purpose for calling this method and also indicates the type of data to return.
        # There are more roles available if needed.
        if role == qtc.Qt.DisplayRole:
            if section < len(self.__header):
                return self.__header[section]
            else:
                return 'Missing Header'

        elif role == qtc.Qt.TextAlignmentRole:
            if section == 0:
                return qtc.Qt.AlignLeft + qtc.Qt.AlignVCenter
            elif section == 1:
                return qtc.Qt.AlignHCenter + qtc.Qt.AlignVCenter
            elif section == 2:
                return qtc.Qt.AlignRight + qtc.Qt.AlignVCenter

        elif role == qtc.Qt.FontRole:
            font = qtg.QFont()
            font.setFamily("MS Shell Dlg 2")
            font.setBold(True)
            font.setPointSize(18)
            font.setUnderline(True)
            return font

        elif role == qtc.Qt.ForegroundRole:
            color = qtg.QColor('#cf2027')
            brush = qtg.QBrush(color)
            return brush

        return None

    def resetData(self, hours_table_model: list):
        self.__data = hours_table_model


class InOutWindow(qtw.QWidget, Ui_InOutWindow):
    """The Check In/Out window contains a Check In button, a Check Out button, a Cancel button,
        and the 'Checked In' List."""

    # Signal to indicate that the Check In/Out window was closed.
    window_closed = qtc.pyqtSignal(str)

    def __init__(self, parent: qtw.QWidget, db_manager: DatabaseManager):
        super().__init__(parent)
        self.setupUi(self)

        # Force the user to interact with this window
        self.setWindowModality(qtc.Qt.ApplicationModal)  # block input to all other windows
        self.setWindowFlag(qtc.Qt.Dialog)                # dialog box without min or max buttons
        self.setWindowFlag(qtc.Qt.FramelessWindowHint)   # borderless window that cannot be resized

        self.__db_manager = db_manager
        self.__barcode = ''
        self.__status = ''

        # Create the Model for the hoursTable
        self.__hours_table_header = ('Day', 'Date', 'Hours')
        self.__hours_table_column_width = (60, 130, 90)  # Needs to be less than 300 total
        self.__table_model = HoursTableModel([('', '', '')], self.__hours_table_header)
        self.hoursTable.setModel(self.__table_model)
        self.hoursTable.setEditTriggers(qtw.QAbstractItemView.NoEditTriggers)
        self.hoursTable.horizontalHeader().setFixedHeight(45)
        self.hoursTable.setSelectionMode(qtw.QAbstractItemView.NoSelection)
        self.hoursTable.setFocusPolicy(qtc.Qt.NoFocus)
        self.hoursTable.setVerticalScrollBarPolicy(qtc.Qt.ScrollBarAlwaysOn)
        self.hoursTable.setHorizontalScrollBarPolicy(qtc.Qt.ScrollBarAlwaysOff)
        self.hoursTable.setAutoScroll(False)
        self.hoursTable.setAutoScrollMargin(400)

        for col in range(len(self.__hours_table_column_width)):
            self.hoursTable.setColumnWidth(col, self.__hours_table_column_width[col])

        # Signals to indicate which button was clicked.
        self.cancelButton.clicked.connect(lambda: self.clicked('Cancel'))
        self.checkinButton.clicked.connect(lambda: self.clicked('Check In'))
        self.checkoutButton.clicked.connect(lambda: self.clicked('Check Out'))

        self.hide()

    def __config_window(self):
        # "data" is a 4-tuple: (firstname, lastname, status, total_hours)
        success, message, data = self.__db_manager.get_student_data(self.__barcode)

        # Set the data to display in the Check In/Out window.
        self.studentName.setText(data[0] + ' ' + data[1])
        self.__status = data[2]
        # self.totalHours.setNum(data[3])

        # The "hours_table_model" is a list of 3-tuples:  [ ('day of week', 'date', 'hours'), ... ]
        success, message, hours_table_model, total_hours = self.__db_manager.get_student_hours_table(self.__barcode)
        self.totalHours.setNum(total_hours)

        if not hours_table_model:
            hours_table_model = [('', '', '')]

        self.__table_model.beginResetModel()
        self.__table_model.resetData(hours_table_model)
        self.__table_model.endResetModel()

        for col in range(len(self.__hours_table_column_width)):
            self.hoursTable.setColumnWidth(col, self.__hours_table_column_width[col])

        # Disable either the Check In or Check Out button.
        if self.__status == 'Checked In':
            self.set_button_state(self.checkinButton, 'Already Checked In', False)
            self.set_button_state(self.checkoutButton, '', True)
        elif self.__status == 'Checked Out':
            self.set_button_state(self.checkinButton, '', True)
            self.set_button_state(self.checkoutButton, 'Not Checked In', False)

    def show_window(self, barcode: str):
        self.__barcode = barcode
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
        if button_name == 'Cancel':
            message = 'Cancelled.'
        elif button_name == 'Check In' and self.__status == 'Checked Out':
            success, message = self.__db_manager.checkin_student(self.__barcode)
        elif button_name == 'Check Out' and self.__status == 'Checked In':
            success, message = self.__db_manager.checkout_student(self.__barcode)
        else:
            message = 'Nothing done.'

        self.window_closed.emit(message)
        self.hide()
        self.__clean_up()

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
        self.__barcode = ''
        self.__status = ''
        self.__table_model.beginResetModel()
        self.__table_model.resetData([('', '', '')])
        self.__table_model.endResetModel()
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
