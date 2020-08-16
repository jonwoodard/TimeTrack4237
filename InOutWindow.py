import logging
from PyQt5 import QtWidgets as qtw
from PyQt5 import QtCore as qtc
from PyQt5 import QtGui as qtg

from gui.Ui_InOutWindow import Ui_InOutWindow
from DatabaseManager import DatabaseManager

logger = logging.getLogger('TimeTrack.InOutWindow')


class InOutWindow(qtw.QWidget, Ui_InOutWindow):
    """The View (GUI) of the Check In/Out Window."""

    # Signal to indicate that the InOutWindow was closed.
    window_closed = qtc.pyqtSignal(str)

    def __init__(self, parent: qtw.QWidget, db_filename: str, barcode: str):
        logger.info(' >> Started')
        super().__init__(parent=parent)
        self.setupUi(self)

        self.__db_manager = DatabaseManager(db_filename)
        success, message, data = self.__db_manager.get_student_data(barcode)

        # Force the user to interact with this window before they can interact with the Main Window.
        self.setWindowModality(qtc.Qt.ApplicationModal)
        self.setWindowFlag(qtc.Qt.Dialog)
        self.setWindowFlag(qtc.Qt.FramelessWindowHint)

        # Set the data to display on the this window.
        self.studentName.setText(data[0])
        self.__status = data[1]
        self.totalHours.setNum(data[2])

        # Create the Model for the hoursTable
        table = {'name': 'Student',
                 'view': self.hoursTable,
                 'header': ('Day', 'Date', 'Hours'),
                 'column_width': (80, 170, 110)}
        button = {'Check In': (self.checkinButton, '', 'Already Checked In'),
                  'Check Out': (self.checkoutButton, '', 'Not Checked In'),
                  'Cancel': (self.cancelButton, '', '')}
        self.hours = self.TableInterface(db_filename, table, button, barcode)

        if self.__status == 'Checked In':
            self.hours.enable_button('Check In', False)
        elif self.__status == 'Checked Out':
            self.hours.enable_button('Check Out', False)

        # Signals to indicate which button was clicked.
        self.hours.button('Cancel').clicked.connect(lambda: self.clicked('Cancel'))
        self.hours.button('Check In').clicked.connect(lambda: self.clicked('Check In'))
        self.hours.button('Check Out').clicked.connect(lambda: self.clicked('Check Out'))

        #if platform.system() == 'Windows':
        #self.show()
        #else:
        self.showFullScreen()

    @qtc.pyqtSlot(str)
    def clicked(self, button_name: str):
        """This slot is called when a button is clicked."""
        logger.debug(f'({button_name}) >> Started')

        # Determine which button was clicked and set the message to be displayed.
        if button_name == 'Cancel':
            message = 'Cancelled.'
        elif button_name == 'Check In' and self.__status == 'Checked Out':
            message = self.hours.table_model.check_in_student()
        elif button_name == 'Check Out' and self.__status == 'Checked In':
            message = self.hours.table_model.check_out_student()
        else:
            message = 'Nothing done.'

        self.window_closed.emit(message)
        self.close()

    class TableInterface:

        def __init__(self, db_filename: str, table: dict, button: dict, barcode: str):
            self.__table = table
            self.__button = button

            self.table_model = TableModel(db_filename, barcode, self.__table['header'])
            self.__table['view'].setModel(self.table_model)
            self.__table['view'].setEditTriggers(qtw.QAbstractItemView.NoEditTriggers)
            self.__table['view'].horizontalHeader().setFixedHeight(45)
            self.__table['view'].setSelectionMode(qtw.QAbstractItemView.NoSelection)
            self.__table['view'].setFocusPolicy(qtc.Qt.NoFocus)
            self.__table['view'].setVerticalScrollBarPolicy(qtc.Qt.ScrollBarAlwaysOn)
            self.__table['view'].setHorizontalScrollBarPolicy(qtc.Qt.ScrollBarAlwaysOff)
            self.__table['view'].setAutoScroll(False)
            self.__table['view'].setAutoScrollMargin(400)
            self.set_column_width()

        def set_column_width(self):
            """This method sets the column widths of the table."""

            for col in range(len(self.__table['column_width'])):
                self.__table['view'].setColumnWidth(col, self.__table['column_width'][col])

        def enable_button(self, button_name: str, enable: bool):
            """This method enables the correct buttons and sets the tool tips font."""

            btn = self.__button.get(button_name, None)
            if btn:
                btn[0].setEnabled(enable)
                if enable:
                    btn[0].setToolTip(btn[1])
                else:
                    font = qtg.QFont()
                    font.setBold(False)
                    font.setPointSize(24)
                    btn[0].setFont(font)
                    btn[0].setToolTip(btn[2])

        def button(self, button_name: str):
            """This method returns the push button with the given button name."""

            btn = self.__button.get(button_name, None)
            if btn:
                return btn[0]
            else:
                return qtw.QPushButton()


class TableModel(qtc.QAbstractTableModel):
    """The Model (data) for the Hours Table on the Check In/Out Window."""

    def __init__(self, db_filename: str, barcode: str, header: tuple):
        super().__init__()

        self.__db_manager = DatabaseManager(db_filename)
        self.__barcode = barcode
        self.__header = header

        # The self.__data attribute is a list of 3-tuples
        # [ ('day of week', 'date', 'hours'), ... ]
        success, message, self.__data = self.__db_manager.get_student_hours_table(self.__barcode)

    def rowCount(self, parent: qtc.QModelIndex = qtc.QModelIndex()):
        """This method overrides the abstract method in the parent class.
        It returns the number of rows in the table."""

        return len(self.__data)

    def columnCount(self, parent: qtc.QModelIndex = qtc.QModelIndex()):
        """This method overrides the abstract method in the parent class.
        It returns the number of columns in the table."""

        if self.__data:
            return len(self.__data[0])
        else:
            return 0

    def headerData(self, section: int, orientation: qtc.Qt.Orientation, role: qtc.Qt.ItemDataRole = qtc.Qt.DisplayRole):
        """This method overrides the abstract method in the parent class.
        It returns the headers and formatting for the horizontal headers."""

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

    def data(self, index: qtc.QModelIndex, role: qtc.Qt.ItemDataRole = qtc.Qt.DisplayRole):
        """This method overrides the abstract method in the parent class.
        It returns the data and formatting for the data."""

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

    def check_in_student(self):
        """This method will check in a student. It returns a message indicating the results of the check in."""
        logger.debug(' >> Started')

        success, message = self.__db_manager.checkin_student(self.__barcode)
        return message

    def check_out_student(self):
        """This method will check out a student. It returns a message indicating the results of the check out."""
        logger.debug(' >> Started')

        success, message = self.__db_manager.checkout_student(self.__barcode)
        return message
