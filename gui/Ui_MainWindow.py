# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'Ui_MainWindow.ui'
#
# Created by: PyQt5 UI code generator 5.15.9
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1024, 600)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/TimeTrackIcon.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        MainWindow.setWindowIcon(icon)
        self.horizontalLayout = QtWidgets.QHBoxLayout(MainWindow)
        self.horizontalLayout.setContentsMargins(10, 10, 10, 10)
        self.horizontalLayout.setSpacing(10)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.barcodeVerticalLayout = QtWidgets.QVBoxLayout()
        self.barcodeVerticalLayout.setContentsMargins(10, 10, 10, 10)
        self.barcodeVerticalLayout.setSpacing(10)
        self.barcodeVerticalLayout.setObjectName("barcodeVerticalLayout")
        spacerItem = QtWidgets.QSpacerItem(0, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        self.barcodeVerticalLayout.addItem(spacerItem)
        self.logoLabel = QtWidgets.QLabel(MainWindow)
        self.logoLabel.setPixmap(QtGui.QPixmap(":/TimeTrackLogo.png"))
        self.logoLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.logoLabel.setObjectName("logoLabel")
        self.barcodeVerticalLayout.addWidget(self.logoLabel)
        spacerItem1 = QtWidgets.QSpacerItem(40, 0, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.barcodeVerticalLayout.addItem(spacerItem1)
        self.barcodeLabel = QtWidgets.QLabel(MainWindow)
        font = QtGui.QFont()
        font.setPointSize(48)
        font.setBold(True)
        self.barcodeLabel.setFont(font)
        self.barcodeLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.barcodeLabel.setObjectName("barcodeLabel")
        self.barcodeVerticalLayout.addWidget(self.barcodeLabel)
        self.message = QtWidgets.QLabel(MainWindow)
        font = QtGui.QFont()
        font.setPointSize(36)
        self.message.setFont(font)
        self.message.setAlignment(QtCore.Qt.AlignCenter)
        self.message.setObjectName("message")
        self.barcodeVerticalLayout.addWidget(self.message)
        self.barcode = QtWidgets.QLineEdit(MainWindow)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.barcode.sizePolicy().hasHeightForWidth())
        self.barcode.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.barcode.setFont(font)
        self.barcode.setText("")
        self.barcode.setMaxLength(30)
        self.barcode.setAlignment(QtCore.Qt.AlignCenter)
        self.barcode.setObjectName("barcode")
        self.barcodeVerticalLayout.addWidget(self.barcode)
        self.horizontalLayout.addLayout(self.barcodeVerticalLayout)
        self.verticalLine = QtWidgets.QFrame(MainWindow)
        self.verticalLine.setBaseSize(QtCore.QSize(0, 0))
        self.verticalLine.setFrameShape(QtWidgets.QFrame.VLine)
        self.verticalLine.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.verticalLine.setObjectName("verticalLine")
        self.horizontalLayout.addWidget(self.verticalLine)
        self.checkedInVerticalLayout = QtWidgets.QVBoxLayout()
        self.checkedInVerticalLayout.setContentsMargins(10, 10, 10, 10)
        self.checkedInVerticalLayout.setSpacing(10)
        self.checkedInVerticalLayout.setObjectName("checkedInVerticalLayout")
        self.checkedInLabel = QtWidgets.QLabel(MainWindow)
        font = QtGui.QFont()
        font.setPointSize(24)
        font.setBold(True)
        self.checkedInLabel.setFont(font)
        self.checkedInLabel.setObjectName("checkedInLabel")
        self.checkedInVerticalLayout.addWidget(self.checkedInLabel)
        self.checkedInList = QtWidgets.QListView(MainWindow)
        self.checkedInList.setMinimumSize(QtCore.QSize(300, 0))
        self.checkedInList.setMaximumSize(QtCore.QSize(375, 16777215))
        font = QtGui.QFont()
        font.setFamily("MS Shell Dlg 2")
        font.setPointSize(18)
        self.checkedInList.setFont(font)
        self.checkedInList.setObjectName("checkedInList")
        self.checkedInVerticalLayout.addWidget(self.checkedInList)
        self.horizontalLayout.addLayout(self.checkedInVerticalLayout)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "TimeTrack4237"))
        self.barcodeLabel.setText(_translate("MainWindow", "Scan Your Barcode"))
        self.checkedInLabel.setText(_translate("MainWindow", "Checked In"))
import resources_rc
