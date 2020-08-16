import logging

from PyQt5 import QtWidgets as qtw
from PyQt5 import QtCore as qtc

from gui.Ui_NumberPadDialogBox import Ui_NumberPadDialogBox

logger = logging.getLogger('TimeTrack.KeypadDialogBox')


class NumberPadDialogBox(qtw.QWidget, Ui_NumberPadDialogBox):
    """This creates a number pad, with the digits 0-9."""

    window_closed = qtc.pyqtSignal(str, str)

    def __init__(self, parent: qtw.QWidget):
        super().__init__(parent=parent)
        self.setupUi(self)

        self.setWindowModality(qtc.Qt.ApplicationModal)
        self.setWindowFlag(qtc.Qt.Dialog)

        self.zero.clicked.connect(lambda: self.number_pressed('0'))
        self.one.clicked.connect(lambda: self.number_pressed('1'))
        self.two.clicked.connect(lambda: self.number_pressed('2'))
        self.three.clicked.connect(lambda: self.number_pressed('3'))
        self.four.clicked.connect(lambda: self.number_pressed('4'))
        self.five.clicked.connect(lambda: self.number_pressed('5'))
        self.six.clicked.connect(lambda: self.number_pressed('6'))
        self.seven.clicked.connect(lambda: self.number_pressed('7'))
        self.eight.clicked.connect(lambda: self.number_pressed('8'))
        self.nine.clicked.connect(lambda: self.number_pressed('9'))
        self.clear.clicked.connect(self.entry.clear)

        self.buttonBox.accepted.connect(lambda: self.dialog_box_button_clicked('OK'))
        self.buttonBox.rejected.connect(lambda: self.dialog_box_button_clicked('Cancel'))
        self.entry.returnPressed.connect(lambda: self.dialog_box_button_clicked('OK'))

        self.show()

    @qtc.pyqtSlot()
    def clear(self):
        self.entry.clear()
        self.entry.setFocus()

    @qtc.pyqtSlot(str)
    def number_pressed(self, number: str):
        current_entry = self.entry.text()
        self.entry.setText(current_entry + number)

    @qtc.pyqtSlot(str)
    def dialog_box_button_clicked(self, button_name: str):
        entry = ''
        if button_name == 'OK':
            entry = self.entry.text()
        self.window_closed.emit(button_name, entry)
        self.close()
