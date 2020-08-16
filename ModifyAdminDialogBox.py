import logging
from PyQt5 import QtWidgets as qtw
from PyQt5 import QtCore as qtc

from gui.Ui_ModifyAdminDialogBox import Ui_ModifyAdminDialogBox

logger = logging.getLogger('TimeTrack.ModifyAdminDialogBox')


class ModifyAdminDialogBox(qtw.QDialog, Ui_ModifyAdminDialogBox):

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

        self.oldPin.setEchoMode(qtw.QLineEdit.Password)
        self.newPin.setEchoMode(qtw.QLineEdit.Password)
        self.verifyPin.setEchoMode(qtw.QLineEdit.Password)

        self.error_message = qtw.QErrorMessage(self)
        self.error_message.setWindowTitle('TimeTrack4237')

        self.buttonBox.accepted.connect(self.yes_clicked)
        self.buttonBox.rejected.connect(self.close)

        self.show()

    def set_title(self):
        title = self.mode + ' ' + self.title.text()
        self.title.setText(title)

    def set_data(self):
        if self.mode in ('Edit', 'Delete', 'Reset PIN'):
            self.barcode.setText(self.data[1])
            self.firstName.setText(self.data[2])
            self.lastName.setText(self.data[3])

    def set_message(self):
        if self.mode == 'Delete':
            self.message.setText('WARNING: This will delete this admin. Delete this admin?')

    def disable_fields(self):
        if self.mode == 'New':
            self.oldPinLabel.setDisabled(True)
            self.oldPin.setDisabled(True)
            self.oldPinLabel.setVisible(False)
            self.oldPin.setVisible(False)
        elif self.mode == 'Edit':
            self.oldPinLabel.setDisabled(True)
            self.oldPin.setDisabled(True)
            self.oldPinLabel.setVisible(False)
            self.oldPin.setVisible(False)
            self.newPinLabel.setDisabled(True)
            self.newPin.setDisabled(True)
            self.newPinLabel.setVisible(False)
            self.newPin.setVisible(False)
            self.verifyPinLabel.setDisabled(True)
            self.verifyPin.setDisabled(True)
            self.verifyPinLabel.setVisible(False)
            self.verifyPin.setVisible(False)
        elif self.mode == 'Delete':
            self.oldPinLabel.setDisabled(True)
            self.oldPin.setDisabled(True)
            self.oldPinLabel.setVisible(False)
            self.oldPin.setVisible(False)
            self.newPinLabel.setDisabled(True)
            self.newPin.setDisabled(True)
            self.newPinLabel.setVisible(False)
            self.newPin.setVisible(False)
            self.verifyPinLabel.setDisabled(True)
            self.verifyPin.setDisabled(True)
            self.verifyPinLabel.setVisible(False)
            self.verifyPin.setVisible(False)
            self.barcode.setDisabled(True)
            self.firstName.setDisabled(True)
            self.lastName.setDisabled(True)
        elif self.mode == 'Reset PIN':
            self.barcode.setDisabled(True)
            self.firstName.setDisabled(True)
            self.lastName.setDisabled(True)

    @qtc.pyqtSlot()
    def yes_clicked(self):
        if self.newPin.text() != self.verifyPin.text():
            self.error_message.showMessage('New PIN field and Verify PIN field do not match.')
            return

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

        if self.mode == 'New' or self.mode == 'Reset PIN':
            old_pin = self.oldPin.text()
            if not old_pin:
                old_pin = None

            new_pin = self.newPin.text()
            if not new_pin:
                new_pin = None

            data += (new_pin, old_pin)
            self.data += (None, None)

        # Check if the new data is different from the original data
        if data != self.data or self.mode == 'Delete':
            self.changes_accepted.emit(self, self.mode, data)
        else:
            self.close()
