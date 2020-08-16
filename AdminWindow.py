import logging
import os
import csv
from PyQt5 import QtWidgets as qtw
from PyQt5 import QtCore as qtc
from PyQt5 import QtGui as qtg

from gui.Ui_AdminWindow import Ui_AdminWindow
from DatabaseManager import DatabaseManager

from ModifyStudentDialogBox import ModifyStudentDialogBox
from ModifyActivityDialogBox import ModifyActivityDialogBox
from ModifyAdminDialogBox import ModifyAdminDialogBox

logger = logging.getLogger('TimeTrack.AdminWindow')


class AdminWindow(qtw.QWidget, Ui_AdminWindow):
    """The View (GUI) of the Admin Window."""

    window_closed = qtc.pyqtSignal()

    def __init__(self, parent: qtw.QWidget, db_filename: str):
        super().__init__(parent)
        self.setupUi(self)

        self.db_filename = db_filename

        # Force the user to interact with this window before they can interact with the Main Window.
        self.setWindowModality(qtc.Qt.ApplicationModal)
        self.setWindowFlag(qtc.Qt.Dialog)
        self.setWindowFlag(qtc.Qt.FramelessWindowHint)
        self.tabWidget.setCurrentIndex(0)

        # Set up the student table model and view
        table = {'name': 'Student',
                 'view': self.studentTable,
                 'header': ('rowid', 'Barcode', 'First Name', 'Last Name'),
                 'column_width': (100, 140, 250, 250)}
        button = {'New': (self.newStudentButton, '', ''),
                  'Edit': (self.editStudentButton, '', 'Select a Student Record'),
                  'Delete': (self.deleteStudentButton, '', 'Select a Student Record'),
                  'Import': (self.importStudentButton, '', '')}
        self.student = self.TableInterface(self.db_filename, table, button)
        self.student.enable_button('Edit', False)
        self.student.enable_button('Delete', False)

        # Set up the activity table model and view
        table = {'name': 'Activity',
                 'view': self.activityTable,
                 'header': ('rowid', 'Barcode', 'Check In', 'Check Out'),
                 'column_width': (100, 140, 300, 300)}
        button = {'New': (self.newActivityButton, '', 'Select a Student Record'),
                  'Edit': (self.editActivityButton, '', 'Select an Activity Record'),
                  'Delete': (self.deleteActivityButton, '', 'Select an Activity Record')}
        self.activity = self.TableInterface(self.db_filename, table, button)
        self.activity.enable_button('New', False)
        self.activity.enable_button('Edit', False)
        self.activity.enable_button('Delete', False)

        # Set up the admin table model and view
        table = {'name': 'Admin',
                 'view': self.adminTable,
                 'header': ('rowid', 'Barcode', 'First Name', 'Last Name'),
                 'column_width': (100, 140, 250, 250)}
        button = {'New': (self.newAdminButton, '', ''),
                  'Edit': (self.editAdminButton, '', 'Select an Admin Record'),
                  'Delete': (self.deleteAdminButton, '', 'Select an Admin Record'),
                  'Reset PIN': (self.resetPinButton, '', 'Select an Admin Record')}
        self.admin = self.TableInterface(self.db_filename, table, button)
        self.admin.enable_button('Edit', False)
        self.admin.enable_button('Delete', False)
        self.admin.enable_button('Reset PIN', False)

        # Signals
        self.closeButton.clicked.connect(self.close_window)

        self.student.button('New').clicked.connect(lambda: self.button_clicked('New', 'Student'))
        self.student.button('Edit').clicked.connect(lambda: self.button_clicked('Edit', 'Student'))
        self.student.button('Delete').clicked.connect(lambda: self.button_clicked('Delete', 'Student'))
        self.student.button('Import').clicked.connect(lambda: self.button_clicked('Import', 'Student'))

        self.activity.button('New').clicked.connect(lambda: self.button_clicked('New', 'Activity'))
        self.activity.button('Edit').clicked.connect(lambda: self.button_clicked('Edit', 'Activity'))
        self.activity.button('Delete').clicked.connect(lambda: self.button_clicked('Delete', 'Activity'))

        self.admin.button('New').clicked.connect(lambda: self.button_clicked('New', 'Admin'))
        self.admin.button('Edit').clicked.connect(lambda: self.button_clicked('Edit', 'Admin'))
        self.admin.button('Delete').clicked.connect(lambda: self.button_clicked('Delete', 'Admin'))
        self.admin.button('Reset PIN').clicked.connect(lambda: self.button_clicked('Reset PIN', 'Admin'))

        self.student.table_selection.selectionChanged.connect(self.student_table_selection_changed)
        self.activity.table_selection.selectionChanged.connect(self.activity_table_selection_changed)
        self.admin.table_selection.selectionChanged.connect(self.admin_table_selection_changed)

        self.showFullScreen()

    @qtc.pyqtSlot()
    def close_window(self):
        """This slot is used to close the window and emit the window_closed signal."""
        logger.debug(' >> Started')

        self.window_closed.emit()
        self.close()

    @qtc.pyqtSlot(str, str)
    def button_clicked(self, button_name: str, table_name: str):
        """This slot is called when a button is clicked."""
        logger.debug(f'({button_name}, {table_name}) >> Started')

        data = tuple()

        if table_name == 'Student':
            if button_name == 'Edit' or button_name == 'Delete':
                index = self.student.table_selection.selectedIndexes()
                data = tuple(item.data() for item in index)

            if button_name in ('New', 'Edit', 'Delete'):
                dialog_box = ModifyStudentDialogBox(self, button_name, data)
                dialog_box.changes_accepted.connect(self.accept_student)
            elif button_name == 'Import':
                csv_filename, _ = qtw.QFileDialog.getOpenFileName(self, 'Open a files', os.getcwd(), 'csv (*.csv)')
                _, file_extension = os.path.splitext(csv_filename)
                if file_extension == '.csv':
                    self.student.table_model.import_data(csv_filename)
                    self.student.set_column_width()
                    self.student.table_selection.clear()
                    self.activity.table_selection.clear()

        elif table_name == 'Activity':
            if button_name == 'New':
                index = self.student.table_selection.selectedIndexes()
                data = ('', index[1].data(), '', '')
            if button_name == 'Edit' or button_name == 'Delete':
                index = self.activity.table_selection.selectedIndexes()
                data = tuple(item.data() for item in index)

            dialog_box = ModifyActivityDialogBox(self, button_name, data)
            dialog_box.changes_accepted.connect(self.accept_activity)

        elif table_name == 'Admin':
            if button_name in ('Edit', 'Delete', 'Reset PIN'):
                index = self.admin.table_selection.selectedIndexes()
                data = tuple(item.data() for item in index)

            dialog_box = ModifyAdminDialogBox(self, button_name, data)
            dialog_box.changes_accepted.connect(self.accept_admin)

    @qtc.pyqtSlot(qtw.QDialog, str, tuple)
    def accept_student(self, dialog_box: qtw.QDialog, mode: str, data: tuple):
        """This slot is called when Modify Student Dialog Box is closed."""

        row_id = data[0]
        record = data[1:]
        success = False
        message = 'Error'

        if mode == 'New':
            success, message = self.student.table_model.new_record(record)
            if success:
                self.activity.table_model.set_filter(record[0])
        elif mode == 'Edit':
            success, message = self.student.table_model.edit_record(row_id, record)
            if success:
                self.activity.table_model.set_filter(record[0])
        elif mode == 'Delete':
            success, message = self.student.table_model.delete_record(row_id)
            if success:
                self.student.table_selection.clear()
                self.activity.table_selection.clear()
                self.activity.table_model.set_filter()

        if success:
            dialog_box.close()
        else:
            dialog_box.error_message.showMessage(message)

        self.student.set_column_width()
        self.activity.set_column_width()

    @qtc.pyqtSlot(qtc.QItemSelection, qtc.QItemSelection)
    def student_table_selection_changed(self, selected: qtc.QItemSelection, deselected: qtc.QItemSelection):
        """This slot is called when the Student Table selection is changed."""

        self.activity.table_selection.clear()
        self.activity.enable_button('Edit', False)
        self.activity.enable_button('Delete', False)

        enable_button = False

        if selected:
            barcode = selected.indexes()[1].data()
            self.activity.table_model.set_filter(barcode)
            enable_button = True

        self.student.enable_button('Edit', enable_button)
        self.student.enable_button('Delete', enable_button)
        self.activity.enable_button('New', enable_button)
        self.student.set_column_width()
        self.activity.set_column_width()

    @qtc.pyqtSlot(qtw.QDialog, str, tuple)
    def accept_activity(self, dialog_box: qtw.QDialog, mode: str, data: tuple):
        """This slot is called when Modify Activity Dialog Box is closed."""

        row_id = data[0]
        record = data[1:]
        success = False
        message = 'Error'

        if mode == 'New':
            success, message = self.activity.table_model.new_record(record)
        elif mode == 'Edit':
            success, message = self.activity.table_model.edit_record(row_id, record)
            if success:
                self.activity.table_selection.clear()
        elif mode == 'Delete':
            success, message = self.activity.table_model.delete_record(row_id)
            if success:
                self.activity.table_selection.clear()

        if success:
            dialog_box.close()
        else:
            dialog_box.error_message.showMessage(message)

        self.student.set_column_width()
        self.activity.set_column_width()

    @qtc.pyqtSlot(qtc.QItemSelection, qtc.QItemSelection)
    def activity_table_selection_changed(self, selected: qtc.QItemSelection, deselected: qtc.QItemSelection):
        """This slot is called when the Activity Table selection is changed."""

        enable_button = False

        if selected:
            enable_button = True

        self.activity.enable_button('Edit', enable_button)
        self.activity.enable_button('Delete', enable_button)
        self.activity.set_column_width()

    @qtc.pyqtSlot(qtw.QDialog, str, tuple)
    def accept_admin(self, dialog_box: qtw.QDialog, mode: str, data: tuple):
        """This slot is called when Modify Admin Dialog Box is closed."""

        row_id = data[0]
        record = data[1:]
        success = False
        message = 'Error'

        if mode == 'New':
            record = record[0:4]
            success, message = self.admin.table_model.new_record(record)
            if success:
                self.admin.table_selection.clear()
        elif mode == 'Edit':
            success, message = self.admin.table_model.edit_record(row_id, record)
        elif mode == 'Delete':
            success, message = self.admin.table_model.delete_record(row_id)
            if success:
                self.admin.table_selection.clear()
        elif mode == 'Reset PIN':
            success, message = self.admin.table_model.reset_pin(row_id, record[3], record[4])

        if success:
            dialog_box.close()
        else:
            dialog_box.error_message.showMessage(message)

    @qtc.pyqtSlot(qtc.QItemSelection, qtc.QItemSelection)
    def admin_table_selection_changed(self, selected: qtc.QItemSelection, deselected: qtc.QItemSelection):
        """This slot is called when the Admin Table selection is changed."""

        enable_button = False

        if selected:
            enable_button = True

        self.admin.enable_button('Edit', enable_button)
        self.admin.enable_button('Delete', enable_button)
        self.admin.enable_button('Reset PIN', enable_button)

        if self.admin.table_model.rowCount() == 1:
            self.admin.enable_button('Delete', False)

        self.admin.set_column_width()

    class TableInterface:

        def __init__(self, db_filename: str, table: dict, button: dict):
            self.__table = table
            self.__button = button

            self.table_model = TableModel(db_filename, self.__table['name'], self.__table['header'])
            self.__table['view'].setModel(self.table_model)
            self.__table['view'].setEditTriggers(qtw.QAbstractItemView.NoEditTriggers)
            self.__table['view'].horizontalHeader().setFixedHeight(60)

            self.table_selection = self.__table['view'].selectionModel()
            self.__table['view'].setSelectionMode(qtw.QAbstractItemView.SingleSelection)
            self.__table['view'].setSelectionBehavior(qtw.QAbstractItemView.SelectRows)
            self.set_column_width()

        def set_column_width(self):
            """This method sets the column widths of the table."""

            for col in range(len(self.__table['column_width'])):
                self.__table['view'].setColumnWidth(col, self.__table['column_width'][col])

        def enable_button(self, button_name: str, enable: bool):
            """This method enables the correct buttons and sets the tool tips."""

            btn = self.__button.get(button_name, None)
            if btn:
                btn[0].setEnabled(enable)
                if enable:
                    btn[0].setToolTip(btn[1])
                else:
                    btn[0].setToolTip(btn[2])

        def button(self, button_name: str):
            """This method returns the push button with the given button name."""

            btn = self.__button.get(button_name, None)
            if btn:
                return btn[0]
            else:
                return qtw.QPushButton()


class TableModel(qtc.QAbstractTableModel):

    def __init__(self, db_filename: str, table: str, header: tuple):
        super().__init__()

        self.__db_manager = DatabaseManager(db_filename)
        self.__table = table
        self.__header = header

        # self.__data is a list of tuples: [('rowid', 'column1', 'column2', 'column3', ...), ... ]
        # The get_table() method returns a 3-tuple: (success, message, [data])
        success, message, self.__data = self.__db_manager.get_table(self.__table)
        self.__filter = None

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
            return qtc.Qt.AlignLeft + qtc.Qt.AlignVCenter

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
        if role == qtc.Qt.DisplayRole or role == qtc.Qt.EditRole:
            if self.__data:
                return self.__data[row][column]
            else:
                return None

        elif role == qtc.Qt.TextAlignmentRole:
            return qtc.Qt.AlignLeft + qtc.Qt.AlignVCenter

        elif role == qtc.Qt.FontRole:
            font = qtg.QFont()
            font.setFamily("MS Shell Dlg 2")
            font.setPointSize(18)
            return font

        return None

    def insertRows(self, position: int, rows: int, parent=qtc.QModelIndex()):
        """This method is used to insert rows in the table view."""

        # This function emits the private rowsAboutToBeInserted() signal
        self.beginInsertRows(parent, position, position + rows - 1)

        for row in range(rows):
            self.__data.insert(position, ('',) * self.columnCount())

        # This function emits the private rowsInserted() signal
        self.endInsertRows()

    def removeRows(self, position: int, rows: int, parent=qtc.QModelIndex()):
        """This method is used to delete rows from the table view."""

        # This function emits the private rowsAboutToBeRemoved() signal
        self.beginRemoveRows(parent, position, position + rows - 1)

        for row in range(rows):
            self.__data.pop(row)

        # This function emits the private rowsRemoved() signal
        self.endRemoveRows()

    def set_filter(self, filter: str = None):
        """This method is used to filter the data in the table view."""

        # This function emits the private signal modelAboutToBeReset()
        self.beginResetModel()

        self.__filter = filter
        # The get_table() method returns a 3-tuple: (success, message, [data])
        success, message, self.__data = self.__db_manager.get_table(self.__table, self.__filter)

        # This function emits the private signal modelReset()
        self.endResetModel()

    def new_record(self, record: tuple):
        """This method creates a new record in the table view."""

        success, message = self.__db_manager.new_record(self.__table, record)

        if success:
            self.insertRows(0, 1)
            # The get_table() method returns a 3-tuple: (success, message, [data])
            success, message, self.__data = self.__db_manager.get_table(self.__table, self.__filter)

        return success, message

    def edit_record(self, row_id: int, record: tuple):
        """This method edits a record in the table view."""

        success, message = self.__db_manager.edit_record(self.__table, row_id, record)

        if success:
            # The get_table() method returns a 3-tuple: (success, message, [data])
            success, message, self.__data = self.__db_manager.get_table(self.__table, self.__filter)

        return success, message

    def delete_record(self, row_id: int):
        """This method deletes a record from the table view."""

        success, message = self.__db_manager.delete_record(self.__table, row_id)

        if success:
            self.removeRows(0, 1)
            # The get_table() method returns a 3-tuple: (success, message, [data])
            success, message, self.__data = self.__db_manager.get_table(self.__table, self.__filter)

        return success, message

    def import_data(self, csv_filename: str):
        """This method imports data from a csv file into"""
        # This function emits the private signal modelAboutToBeReset()
        self.beginResetModel()

        with open(csv_filename, 'r') as fh:
            csv_reader = csv.reader(fh)
            for record in csv_reader:
                self.new_record(tuple(record))

        # The get_table() method returns a 3-tuple: (success, message, [data])
        success, message, self.__data = self.__db_manager.get_table(self.__table)

        # This function emits the private signal modelReset()
        self.endResetModel()

    def reset_pin(self, row_id: int, new_pin: str, old_pin: str):
        """This method resets the admi pin."""

        success, message = self.__db_manager.reset_pin(row_id, new_pin, old_pin)
        return success, message
