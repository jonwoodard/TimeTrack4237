import logging
from PyQt5 import QtWidgets as qtw
from PyQt5 import QtCore as qtc
from PyQt5 import QtGui as qtg

from gui.Ui_InOutWindow import Ui_InOutWindow
from DatabaseManager import DatabaseManager

logger = logging.getLogger('TimeTrack.InOutWindow')


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
            font.setPointSize(18)
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
            font.setPointSize(20)
            font.setUnderline(True)
            return font

        elif role == qtc.Qt.ForegroundRole:
            color = qtg.QColor('#cf2027')
            brush = qtg.QBrush(color)
            return brush

        return None


class InOutWindow(qtw.QWidget, Ui_InOutWindow):
    """The Check In/Out window contains a Check In button, a Check Out button, a Cancel button,
        and the Hours Logged table."""

    # Signal to indicate that the Check In/Out window was closed.
    window_closed = qtc.pyqtSignal(str)

    def __init__(self, parent: qtw.QWidget, db_filename: str, barcode: str):
        logger.info(' >> Started')
        super().__init__(parent)
        self.setupUi(self)

        # Force the user to interact with this window
        self.setWindowModality(qtc.Qt.ApplicationModal)  # block input to all other windows
        self.setWindowFlag(qtc.Qt.Dialog)                # dialog box without min or max buttons
        self.setWindowFlag(qtc.Qt.FramelessWindowHint)   # borderless window that cannot be resized

        self.__db_manager = DatabaseManager(db_filename)
        self.__barcode = barcode

        # "data" is a 4-tuple: (firstname, lastname, status, total_hours)
        success, message, data = self.__db_manager.get_student_data(self.__barcode)

        # Set the data to display in the Check In/Out window.
        self.studentName.setText(data[0] + ' ' + data[1])
        self.__status = data[2]
        self.totalHours.setNum(data[3])

        # The "hours_table_model" is a list of 3-tuples:  [ ('day of week', 'date', 'hours'), ... ]
        success, message, hours_table_model, total_hours = self.__db_manager.get_student_hours_table(self.__barcode)
        self.totalHours.setNum(total_hours)

        # Create the Model for the hoursTable
        hours_table_header = ('Day', 'Date', 'Hours')
        hours_table_column_width = (80, 170, 110)
        # hours_table_columns = {'header': ('Day', 'Date', 'Hours'), 'column_width': (80, 170, 110)}
        self.table_model = HoursTableModel(hours_table_model, hours_table_header)
        self.hoursTable.setModel(self.table_model)
        self.hoursTable.setEditTriggers(qtw.QAbstractItemView.NoEditTriggers)
        self.hoursTable.horizontalHeader().setFixedHeight(45)
        self.hoursTable.setSelectionMode(qtw.QAbstractItemView.NoSelection)
        self.hoursTable.setFocusPolicy(qtc.Qt.NoFocus)
        self.hoursTable.setVerticalScrollBarPolicy(qtc.Qt.ScrollBarAlwaysOn)
        self.hoursTable.setHorizontalScrollBarPolicy(qtc.Qt.ScrollBarAlwaysOff)
        self.hoursTable.setAutoScroll(False)
        self.hoursTable.setAutoScrollMargin(400)

        for col in range(len(hours_table_column_width)):
            self.hoursTable.setColumnWidth(col, hours_table_column_width[col])

        # Disable either the Check In or Check Out button.
        if self.__status == 'Checked In':
            self.disable_button(self.checkinButton, 'Already Checked In')
        elif self.__status == 'Checked Out':
            self.disable_button(self.checkoutButton, 'Not Checked In')

        # Signals to indicate which button was clicked.
        self.cancelButton.clicked.connect(lambda: self.clicked('Cancel'))
        self.checkinButton.clicked.connect(lambda: self.clicked('Check In'))
        self.checkoutButton.clicked.connect(lambda: self.clicked('Check Out'))

        #if platform.system() == 'Windows':
        #self.show()
        #else:
        self.showFullScreen()

    @qtc.pyqtSlot(str)
    def clicked(self, button_name: str) -> None:
        """
        This slot is called when a button is clicked.

        :param button_name: the name of the button clicked
        :return: None, emits the "window_closed" signal and passes a message to display on the Main window
        """
        logger.debug(f'({button_name}) >> Started')

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
        self.close()

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
