# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'Ui_AdminWindow.ui'
#
# Created by: PyQt5 UI code generator 5.15.0
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_AdminWindow(object):
    def setupUi(self, AdminWindow):
        AdminWindow.setObjectName("AdminWindow")
        AdminWindow.resize(1024, 600)
        self.horizontalLayout = QtWidgets.QHBoxLayout(AdminWindow)
        self.horizontalLayout.setContentsMargins(10, 10, 10, 10)
        self.horizontalLayout.setSpacing(10)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.AdminVerticalLayout = QtWidgets.QVBoxLayout()
        self.AdminVerticalLayout.setContentsMargins(10, 10, 10, 10)
        self.AdminVerticalLayout.setSpacing(10)
        self.AdminVerticalLayout.setObjectName("AdminVerticalLayout")
        spacerItem = QtWidgets.QSpacerItem(0, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        self.AdminVerticalLayout.addItem(spacerItem)
        self.logoLabel = QtWidgets.QLabel(AdminWindow)
        self.logoLabel.setPixmap(QtGui.QPixmap(":/TimeTrackLogo.png"))
        self.logoLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.logoLabel.setObjectName("logoLabel")
        self.AdminVerticalLayout.addWidget(self.logoLabel)
        spacerItem1 = QtWidgets.QSpacerItem(40, 0, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.AdminVerticalLayout.addItem(spacerItem1)
        self.adminName = QtWidgets.QLabel(AdminWindow)
        font = QtGui.QFont()
        font.setPointSize(36)
        font.setBold(True)
        font.setWeight(75)
        self.adminName.setFont(font)
        self.adminName.setStyleSheet("color: #cf2027")
        self.adminName.setAlignment(QtCore.Qt.AlignCenter)
        self.adminName.setObjectName("adminName")
        self.AdminVerticalLayout.addWidget(self.adminName)
        self.AdminButtonHorizontalLayout = QtWidgets.QHBoxLayout()
        self.AdminButtonHorizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.AdminButtonHorizontalLayout.setSpacing(0)
        self.AdminButtonHorizontalLayout.setObjectName("AdminButtonHorizontalLayout")
        spacerItem2 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.AdminButtonHorizontalLayout.addItem(spacerItem2)
        self.uploadDataButton = QtWidgets.QPushButton(AdminWindow)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.uploadDataButton.sizePolicy().hasHeightForWidth())
        self.uploadDataButton.setSizePolicy(sizePolicy)
        self.uploadDataButton.setMinimumSize(QtCore.QSize(300, 200))
        font = QtGui.QFont()
        font.setPointSize(26)
        font.setBold(True)
        font.setWeight(75)
        self.uploadDataButton.setFont(font)
        self.uploadDataButton.setFocusPolicy(QtCore.Qt.ClickFocus)
        self.uploadDataButton.setObjectName("uploadDataButton")
        self.AdminButtonHorizontalLayout.addWidget(self.uploadDataButton)
        spacerItem3 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Minimum)
        self.AdminButtonHorizontalLayout.addItem(spacerItem3)
        self.checkOutAllButton = QtWidgets.QPushButton(AdminWindow)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.checkOutAllButton.sizePolicy().hasHeightForWidth())
        self.checkOutAllButton.setSizePolicy(sizePolicy)
        self.checkOutAllButton.setMinimumSize(QtCore.QSize(300, 200))
        font = QtGui.QFont()
        font.setPointSize(26)
        font.setBold(True)
        font.setWeight(75)
        self.checkOutAllButton.setFont(font)
        self.checkOutAllButton.setFocusPolicy(QtCore.Qt.ClickFocus)
        self.checkOutAllButton.setObjectName("checkOutAllButton")
        self.AdminButtonHorizontalLayout.addWidget(self.checkOutAllButton)
        spacerItem4 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.AdminButtonHorizontalLayout.addItem(spacerItem4)
        self.AdminButtonHorizontalLayout.setStretch(0, 1)
        self.AdminButtonHorizontalLayout.setStretch(1, 2)
        self.AdminButtonHorizontalLayout.setStretch(3, 2)
        self.AdminButtonHorizontalLayout.setStretch(4, 1)
        self.AdminVerticalLayout.addLayout(self.AdminButtonHorizontalLayout)
        self.cancelHorizontalLayout = QtWidgets.QHBoxLayout()
        self.cancelHorizontalLayout.setSpacing(0)
        self.cancelHorizontalLayout.setObjectName("cancelHorizontalLayout")
        spacerItem5 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.cancelHorizontalLayout.addItem(spacerItem5)
        self.cancelButton = QtWidgets.QPushButton(AdminWindow)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.cancelButton.sizePolicy().hasHeightForWidth())
        self.cancelButton.setSizePolicy(sizePolicy)
        self.cancelButton.setMinimumSize(QtCore.QSize(200, 100))
        font = QtGui.QFont()
        font.setPointSize(30)
        font.setBold(True)
        font.setWeight(75)
        self.cancelButton.setFont(font)
        self.cancelButton.setFocusPolicy(QtCore.Qt.ClickFocus)
        self.cancelButton.setObjectName("cancelButton")
        self.cancelHorizontalLayout.addWidget(self.cancelButton)
        spacerItem6 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.cancelHorizontalLayout.addItem(spacerItem6)
        self.cancelHorizontalLayout.setStretch(0, 3)
        self.cancelHorizontalLayout.setStretch(1, 2)
        self.cancelHorizontalLayout.setStretch(2, 3)
        self.AdminVerticalLayout.addLayout(self.cancelHorizontalLayout)
        self.horizontalLayout.addLayout(self.AdminVerticalLayout)
        self.verticalLine = QtWidgets.QFrame(AdminWindow)
        self.verticalLine.setBaseSize(QtCore.QSize(0, 0))
        self.verticalLine.setFrameShape(QtWidgets.QFrame.VLine)
        self.verticalLine.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.verticalLine.setObjectName("verticalLine")
        self.horizontalLayout.addWidget(self.verticalLine)
        self.checkedInVerticalLayout = QtWidgets.QVBoxLayout()
        self.checkedInVerticalLayout.setContentsMargins(10, 10, 10, 10)
        self.checkedInVerticalLayout.setSpacing(10)
        self.checkedInVerticalLayout.setObjectName("checkedInVerticalLayout")
        self.checkedInHorizontalLayout = QtWidgets.QHBoxLayout()
        self.checkedInHorizontalLayout.setSpacing(0)
        self.checkedInHorizontalLayout.setObjectName("checkedInHorizontalLayout")
        self.checkedInLabel = QtWidgets.QLabel(AdminWindow)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.checkedInLabel.sizePolicy().hasHeightForWidth())
        self.checkedInLabel.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setPointSize(24)
        font.setBold(True)
        font.setWeight(75)
        self.checkedInLabel.setFont(font)
        self.checkedInLabel.setObjectName("checkedInLabel")
        self.checkedInHorizontalLayout.addWidget(self.checkedInLabel)
        self.checkedInVerticalLayout.addLayout(self.checkedInHorizontalLayout)
        self.checkedInTable = QtWidgets.QListView(AdminWindow)
        self.checkedInTable.setMaximumSize(QtCore.QSize(380, 16777215))
        font = QtGui.QFont()
        font.setFamily("MS Shell Dlg 2")
        font.setPointSize(18)
        self.checkedInTable.setFont(font)
        self.checkedInTable.setObjectName("checkedInTable")
        self.checkedInVerticalLayout.addWidget(self.checkedInTable)
        self.horizontalLayout.addLayout(self.checkedInVerticalLayout)

        self.retranslateUi(AdminWindow)
        QtCore.QMetaObject.connectSlotsByName(AdminWindow)

    def retranslateUi(self, AdminWindow):
        _translate = QtCore.QCoreApplication.translate
        AdminWindow.setWindowTitle(_translate("AdminWindow", "TimeTrack4237"))
        self.uploadDataButton.setText(_translate("AdminWindow", "Upload Data"))
        self.checkOutAllButton.setText(_translate("AdminWindow", "  Check Out ALL"))
        self.cancelButton.setText(_translate("AdminWindow", "Cancel"))
        self.checkedInLabel.setText(_translate("AdminWindow", "Checked In"))
import resources_rc