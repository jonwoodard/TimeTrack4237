from PyQt5 import QtWidgets as qtw
from PyQt5 import QtCore as qtc
from gui.Ui_NumberPadDialogBox import Ui_NumberPadDialogBox


class NumberPadDialogBox(qtw.QDialog, Ui_NumberPadDialogBox):
    """This creates a number pad, with the digits 0-9, along with Clear, OK, and Cancel buttons."""

    # Signal emitted when this dialog box is closed
    window_closed = qtc.pyqtSignal(str)

    def __init__(self, parent: qtw.QWidget):
        super().__init__(parent)
        self.setupUi(self)

        self.setWindowModality(qtc.Qt.ApplicationModal)  # block input to all other windows
        self.overrideWindowFlags(qtc.Qt.Dialog)          # remove all window flags, reset to basic dialog box
        self.setWindowFlag(qtc.Qt.CustomizeWindowHint)   # turn off default window title bar
        self.setWindowFlag(qtc.Qt.WindowTitleHint)       # add a title bar
        self.setWindowFlag(qtc.Qt.WindowSystemMenuHint)  # add the icon in the title bar and close button

        self.buttonBox.button(qtw.QDialogButtonBox.Ok).setEnabled(False)
        self.clear.setEnabled(False)

        # Signal for every button, all connected to the same slot but with a different button name
        self.zero.clicked.connect(lambda: self.button_clicked('0'))
        self.one.clicked.connect(lambda: self.button_clicked('1'))
        self.two.clicked.connect(lambda: self.button_clicked('2'))
        self.three.clicked.connect(lambda: self.button_clicked('3'))
        self.four.clicked.connect(lambda: self.button_clicked('4'))
        self.five.clicked.connect(lambda: self.button_clicked('5'))
        self.six.clicked.connect(lambda: self.button_clicked('6'))
        self.seven.clicked.connect(lambda: self.button_clicked('7'))
        self.eight.clicked.connect(lambda: self.button_clicked('8'))
        self.nine.clicked.connect(lambda: self.button_clicked('9'))
        self.clear.clicked.connect(lambda: self.button_clicked('Clear'))

        self.buttonBox.accepted.connect(lambda: self.button_clicked('OK'))
        self.buttonBox.rejected.connect(lambda: self.button_clicked('Cancel'))

        # Use textChanged to emit the signal whenever the text is changed, including when setText() is called.
        self.entry.textChanged.connect(self.entry_text_edited)
        self.entry.returnPressed.connect(lambda: self.button_clicked('Enter'))

        self.show()

    @qtc.pyqtSlot(str)
    def button_clicked(self, button_name: str) -> None:
        """
        This slot is called when a button is clicked or user presses Enter.
        :param button_name: the name of the button clicked
        :return: None, emits 'window_closed' signal when the dialog box is closed
        """

        if button_name in [str(x) for x in range(10)]:       # buttons '0' through '9'
            entry = self.entry.text()
            self.entry.setText(entry + button_name)
            self.entry.setFocus()

        elif button_name == 'Clear':
            self.entry.clear()
            self.entry.setFocus()

        elif button_name in ['OK', 'Enter']:
            entry = self.entry.text() or ''
            self.window_closed.emit(entry)
            self.close()

        elif button_name == 'Cancel':
            self.entry.clear()
            self.entry.setFocus()
            self.window_closed.emit('')
            self.close()

    @qtc.pyqtSlot()
    def entry_text_edited(self) -> None:
        """
        This slot is called when the entry is edited by the user to enable or disable the OK and Clear buttons.

        :return: None
        """
        if self.entry.text():
            self.buttonBox.button(qtw.QDialogButtonBox.Ok).setEnabled(True)
            self.clear.setEnabled(True)

        else:
            self.buttonBox.button(qtw.QDialogButtonBox.Ok).setEnabled(False)
            self.clear.setEnabled(False)
