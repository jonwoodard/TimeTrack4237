import logging
from PyQt5 import QtWidgets as qtw
from PyQt5 import QtCore as qtc
from datetime import datetime

from gui.Ui_ModifyActivityDialogBox import Ui_ModifyActivityDialogBox

logger = logging.getLogger('TimeTrack.ModifyActivityDialogBox')


class ModifyActivityDialogBox(qtw.QDialog, Ui_ModifyActivityDialogBox):

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

        self.checkOut.setSpecialValueText('None')

        self.error_message = qtw.QErrorMessage(self)
        self.error_message.setWindowTitle('TimeTrack4237')

        self.buttonBox.accepted.connect(self.yes_clicked)
        self.buttonBox.rejected.connect(self.close)

        self.show()

    def set_title(self):
        """This method is used to set the title."""

        title = self.mode + ' ' + self.title.text()
        self.title.setText(title)

    def set_data(self):
        self.barcode.setText(self.data[1])

        if self.mode == 'New':
            date = datetime.now().date()
            self.date.setDate(date)
            in_time = datetime.now().time()
            self.checkIn.setTime(in_time)

        elif self.mode == 'Edit' or self.mode == 'Delete':
            check_in_date = self.data[2].split()[0]
            date = datetime.strptime(check_in_date, '%Y-%m-%d').date()
            self.date.setDate(date)

            check_in_time = self.data[2].split()[1]
            in_time = datetime.strptime(check_in_time, '%H:%M:%S').time()
            self.checkIn.setTime(in_time)

            if self.data[3]:
                check_out_time = self.data[3].split()[1]
                out_time = datetime.strptime(check_out_time, '%H:%M:%S').time()
                self.checkOut.setTime(out_time)
            else:
                self.checkOut.setSpecialValueText('None')

    def set_message(self):
        if self.mode == 'Delete':
            self.message.setText('WARNING: This will delete this activity. Save changes?')

    def disable_fields(self):
        self.barcode.setDisabled(True)

        if self.mode == 'Delete':
            self.date.setDisabled(True)
            self.checkIn.setDisabled(True)
            self.checkOut.setDisabled(True)

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

        date = self.date.text()
        if not date:
            date = None

        check_in = self.checkIn.text()
        if not check_in:
            check_in = None
        else:
            check_in = date + ' ' + check_in

        check_out = self.checkOut.text()
        if not check_out or check_out == 'None':
            check_out = None
        else:
            check_out = date + ' ' + check_out

        data = (row_id, barcode, check_in, check_out)

        # Check if the new data is different from the original data
        if data != self.data or self.mode == 'Delete':
            self.changes_accepted.emit(self, self.mode, data)
        else:
            self.close()
