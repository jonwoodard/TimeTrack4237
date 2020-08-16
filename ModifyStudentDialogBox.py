import logging
from PyQt5 import QtWidgets as qtw
from PyQt5 import QtCore as qtc

from gui.Ui_ModifyStudentDialogBox import Ui_ModifyStudentDialogBox

logger = logging.getLogger('TimeTrack.ModifyStudentDialogBox')


class ModifyStudentDialogBox(qtw.QDialog, Ui_ModifyStudentDialogBox):

    changes_accepted = qtc.pyqtSignal(qtw.QDialog, str, tuple)

    def __init__(self, parent: qtw.QWidget, mode: str, data: tuple):
        super().__init__(parent)
        self.setupUi(self)

        self.mode = mode
        if not data:
            data = (None, None, None, None)
        self.data = data

        self.set_title()
        self.set_data()
        self.set_message()
        self.disable_fields()

        # Force the user to interact with this window before they can interact with the Main Window.
        self.setWindowModality(qtc.Qt.ApplicationModal)
        self.setWindowFlag(qtc.Qt.Dialog)

        self.error_message = qtw.QErrorMessage(self)
        self.error_message.setWindowTitle('TimeTrack4237')

        self.buttonBox.accepted.connect(self.yes_clicked)
        self.buttonBox.rejected.connect(self.close)

        self.show()

    def set_title(self):
        title = self.mode + ' ' + self.title.text()
        self.title.setText(title)

    def set_data(self):
        if self.mode == 'Edit' or self.mode == 'Delete':
            self.barcode.setText(self.data[1])
            self.firstName.setText(self.data[2])
            self.lastName.setText(self.data[3])

    def set_message(self):
        if self.mode == 'Delete':
            self.message.setText('WARNING: This will also delete all records in the Activity Table with this barcode. Delete this student?')

    def disable_fields(self):
        if self.mode == 'Delete':
            self.barcode.setDisabled(True)
            self.firstName.setDisabled(True)
            self.lastName.setDisabled(True)

    @qtc.pyqtSlot()
    def yes_clicked(self):
        # If the field is empty, set the field to None so that the database will set those fields to NULL.
        if self.data:
            row_id = self.data[0]
        else:
            row_id = None

        barcode = self.barcode.text()
        if not barcode:
            barcode = None

        first_name = self.firstName.text()
        if not first_name:
            first_name = None

        last_name = self.lastName.text()
        if not last_name:
            last_name = None

        data = (row_id, barcode, first_name, last_name)

        # Check if the new data is different from the original data
        if data != self.data or self.mode == 'Delete':
            self.changes_accepted.emit(self, self.mode, data)
        else:
            self.close()

