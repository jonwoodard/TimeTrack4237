# -*- coding: utf-8 -*-

# Form implementation generated from reading ui files 'Ui_ModifyStudentDialogBox.ui'
#
# Created by: PyQt5 UI code generator 5.15.0
#
# WARNING: Any manual changes made to this files will be lost when pyuic5 is
# run again.  Do not edit this files unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_ModifyStudentDialogBox(object):
    def setupUi(self, ModifyStudentDialogBox):
        ModifyStudentDialogBox.setObjectName("ModifyStudentDialogBox")
        ModifyStudentDialogBox.resize(500, 400)
        self.verticalLayout = QtWidgets.QVBoxLayout(ModifyStudentDialogBox)
        self.verticalLayout.setObjectName("verticalLayout")
        self.title = QtWidgets.QLabel(ModifyStudentDialogBox)
        font = QtGui.QFont()
        font.setPointSize(24)
        font.setBold(True)
        font.setWeight(75)
        self.title.setFont(font)
        self.title.setObjectName("title")
        self.verticalLayout.addWidget(self.title)
        self.formLayout = QtWidgets.QFormLayout()
        self.formLayout.setObjectName("formLayout")
        self.barcodeLabel = QtWidgets.QLabel(ModifyStudentDialogBox)
        font = QtGui.QFont()
        font.setPointSize(20)
        self.barcodeLabel.setFont(font)
        self.barcodeLabel.setObjectName("barcodeLabel")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.barcodeLabel)
        self.barcode = QtWidgets.QLineEdit(ModifyStudentDialogBox)
        font = QtGui.QFont()
        font.setPointSize(20)
        self.barcode.setFont(font)
        self.barcode.setObjectName("barcode")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.barcode)
        self.firstNameLabel = QtWidgets.QLabel(ModifyStudentDialogBox)
        font = QtGui.QFont()
        font.setPointSize(20)
        self.firstNameLabel.setFont(font)
        self.firstNameLabel.setObjectName("firstNameLabel")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.firstNameLabel)
        self.firstName = QtWidgets.QLineEdit(ModifyStudentDialogBox)
        font = QtGui.QFont()
        font.setPointSize(20)
        self.firstName.setFont(font)
        self.firstName.setObjectName("firstName")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.firstName)
        self.lastNameLabel = QtWidgets.QLabel(ModifyStudentDialogBox)
        font = QtGui.QFont()
        font.setPointSize(20)
        self.lastNameLabel.setFont(font)
        self.lastNameLabel.setObjectName("lastNameLabel")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.lastNameLabel)
        self.lastName = QtWidgets.QLineEdit(ModifyStudentDialogBox)
        font = QtGui.QFont()
        font.setPointSize(20)
        self.lastName.setFont(font)
        self.lastName.setObjectName("lastName")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.lastName)
        self.verticalLayout.addLayout(self.formLayout)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        self.message = QtWidgets.QLabel(ModifyStudentDialogBox)
        font = QtGui.QFont()
        font.setPointSize(20)
        font.setBold(False)
        font.setWeight(50)
        self.message.setFont(font)
        self.message.setWordWrap(True)
        self.message.setObjectName("message")
        self.verticalLayout.addWidget(self.message)
        self.buttonBox = QtWidgets.QDialogButtonBox(ModifyStudentDialogBox)
        font = QtGui.QFont()
        font.setPointSize(20)
        self.buttonBox.setFont(font)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.No|QtWidgets.QDialogButtonBox.Yes)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)
        self.barcodeLabel.setBuddy(self.barcode)
        self.firstNameLabel.setBuddy(self.firstName)
        self.lastNameLabel.setBuddy(self.lastName)

        self.retranslateUi(ModifyStudentDialogBox)
        QtCore.QMetaObject.connectSlotsByName(ModifyStudentDialogBox)

    def retranslateUi(self, ModifyStudentDialogBox):
        _translate = QtCore.QCoreApplication.translate
        ModifyStudentDialogBox.setWindowTitle(_translate("ModifyStudentDialogBox", "TimeTrack4237"))
        self.title.setText(_translate("ModifyStudentDialogBox", "Student"))
        self.barcodeLabel.setText(_translate("ModifyStudentDialogBox", "&Barcode"))
        self.firstNameLabel.setText(_translate("ModifyStudentDialogBox", "&First Name"))
        self.lastNameLabel.setText(_translate("ModifyStudentDialogBox", "&Last Name"))
        self.message.setText(_translate("ModifyStudentDialogBox", "Save changes?"))
