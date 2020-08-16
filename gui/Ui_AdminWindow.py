# -*- coding: utf-8 -*-

# Form implementation generated from reading ui files 'Ui_AdminWindow.ui'
#
# Created by: PyQt5 UI code generator 5.15.0
#
# WARNING: Any manual changes made to this files will be lost when pyuic5 is
# run again.  Do not edit this files unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_AdminWindow(object):
    def setupUi(self, AdminWindow):
        AdminWindow.setObjectName("AdminWindow")
        AdminWindow.resize(1024, 650)
        self.adminWindowVerticalLayout = QtWidgets.QVBoxLayout(AdminWindow)
        self.adminWindowVerticalLayout.setContentsMargins(10, 10, 10, 10)
        self.adminWindowVerticalLayout.setSpacing(10)
        self.adminWindowVerticalLayout.setObjectName("adminWindowVerticalLayout")
        self.tabWidget = QtWidgets.QTabWidget(AdminWindow)
        font = QtGui.QFont()
        font.setPointSize(24)
        self.tabWidget.setFont(font)
        self.tabWidget.setObjectName("tabWidget")
        self.tablesTab = QtWidgets.QWidget()
        self.tablesTab.setObjectName("tablesTab")
        self.tablesTabHLayout = QtWidgets.QHBoxLayout(self.tablesTab)
        self.tablesTabHLayout.setContentsMargins(10, 10, 10, 10)
        self.tablesTabHLayout.setSpacing(10)
        self.tablesTabHLayout.setObjectName("tablesTabHLayout")
        self.studentTableVLayout = QtWidgets.QVBoxLayout()
        self.studentTableVLayout.setSpacing(10)
        self.studentTableVLayout.setObjectName("studentTableVLayout")
        self.studentTableLabel = QtWidgets.QLabel(self.tablesTab)
        self.studentTableLabel.setObjectName("studentTableLabel")
        self.studentTableVLayout.addWidget(self.studentTableLabel)
        self.studentTable = QtWidgets.QTableView(self.tablesTab)
        self.studentTable.setObjectName("studentTable")
        self.studentTableVLayout.addWidget(self.studentTable)
        self.studentButtonsHLayout = QtWidgets.QHBoxLayout()
        self.studentButtonsHLayout.setSpacing(10)
        self.studentButtonsHLayout.setObjectName("studentButtonsHLayout")
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.studentButtonsHLayout.addItem(spacerItem)
        self.newStudentButton = QtWidgets.QPushButton(self.tablesTab)
        font = QtGui.QFont()
        font.setPointSize(20)
        self.newStudentButton.setFont(font)
        self.newStudentButton.setObjectName("newStudentButton")
        self.studentButtonsHLayout.addWidget(self.newStudentButton)
        self.editStudentButton = QtWidgets.QPushButton(self.tablesTab)
        font = QtGui.QFont()
        font.setPointSize(20)
        self.editStudentButton.setFont(font)
        self.editStudentButton.setObjectName("editStudentButton")
        self.studentButtonsHLayout.addWidget(self.editStudentButton)
        self.deleteStudentButton = QtWidgets.QPushButton(self.tablesTab)
        font = QtGui.QFont()
        font.setPointSize(20)
        self.deleteStudentButton.setFont(font)
        self.deleteStudentButton.setObjectName("deleteStudentButton")
        self.studentButtonsHLayout.addWidget(self.deleteStudentButton)
        self.importStudentButton = QtWidgets.QPushButton(self.tablesTab)
        font = QtGui.QFont()
        font.setPointSize(20)
        self.importStudentButton.setFont(font)
        self.importStudentButton.setObjectName("importStudentButton")
        self.studentButtonsHLayout.addWidget(self.importStudentButton)
        self.studentTableVLayout.addLayout(self.studentButtonsHLayout)
        self.tablesTabHLayout.addLayout(self.studentTableVLayout)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.tablesTabHLayout.addItem(spacerItem1)
        self.activityTableVLayout = QtWidgets.QVBoxLayout()
        self.activityTableVLayout.setSpacing(10)
        self.activityTableVLayout.setObjectName("activityTableVLayout")
        self.activityTableLabel = QtWidgets.QLabel(self.tablesTab)
        self.activityTableLabel.setObjectName("activityTableLabel")
        self.activityTableVLayout.addWidget(self.activityTableLabel)
        self.activityTable = QtWidgets.QTableView(self.tablesTab)
        self.activityTable.setObjectName("activityTable")
        self.activityTableVLayout.addWidget(self.activityTable)
        self.activityButtonsHLayout = QtWidgets.QHBoxLayout()
        self.activityButtonsHLayout.setSpacing(10)
        self.activityButtonsHLayout.setObjectName("activityButtonsHLayout")
        spacerItem2 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.activityButtonsHLayout.addItem(spacerItem2)
        self.newActivityButton = QtWidgets.QPushButton(self.tablesTab)
        font = QtGui.QFont()
        font.setPointSize(20)
        self.newActivityButton.setFont(font)
        self.newActivityButton.setObjectName("newActivityButton")
        self.activityButtonsHLayout.addWidget(self.newActivityButton)
        self.editActivityButton = QtWidgets.QPushButton(self.tablesTab)
        font = QtGui.QFont()
        font.setPointSize(20)
        self.editActivityButton.setFont(font)
        self.editActivityButton.setObjectName("editActivityButton")
        self.activityButtonsHLayout.addWidget(self.editActivityButton)
        self.deleteActivityButton = QtWidgets.QPushButton(self.tablesTab)
        font = QtGui.QFont()
        font.setPointSize(20)
        self.deleteActivityButton.setFont(font)
        self.deleteActivityButton.setObjectName("deleteActivityButton")
        self.activityButtonsHLayout.addWidget(self.deleteActivityButton)
        self.activityTableVLayout.addLayout(self.activityButtonsHLayout)
        self.tablesTabHLayout.addLayout(self.activityTableVLayout)
        self.tablesTabHLayout.setStretch(0, 9)
        self.tablesTabHLayout.setStretch(1, 1)
        self.tablesTabHLayout.setStretch(2, 10)
        self.tabWidget.addTab(self.tablesTab, "")
        self.adminTab = QtWidgets.QWidget()
        self.adminTab.setObjectName("adminTab")
        self.adminTabHLayout = QtWidgets.QHBoxLayout(self.adminTab)
        self.adminTabHLayout.setContentsMargins(10, 10, 10, 10)
        self.adminTabHLayout.setSpacing(10)
        self.adminTabHLayout.setObjectName("adminTabHLayout")
        self.adminTableVLayout = QtWidgets.QVBoxLayout()
        self.adminTableVLayout.setSpacing(10)
        self.adminTableVLayout.setObjectName("adminTableVLayout")
        self.adminTableLabel = QtWidgets.QLabel(self.adminTab)
        self.adminTableLabel.setObjectName("adminTableLabel")
        self.adminTableVLayout.addWidget(self.adminTableLabel)
        self.adminTable = QtWidgets.QTableView(self.adminTab)
        self.adminTable.setObjectName("adminTable")
        self.adminTableVLayout.addWidget(self.adminTable)
        self.adminButtonsHLayout = QtWidgets.QHBoxLayout()
        self.adminButtonsHLayout.setSpacing(10)
        self.adminButtonsHLayout.setObjectName("adminButtonsHLayout")
        spacerItem3 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.adminButtonsHLayout.addItem(spacerItem3)
        self.newAdminButton = QtWidgets.QPushButton(self.adminTab)
        font = QtGui.QFont()
        font.setPointSize(20)
        self.newAdminButton.setFont(font)
        self.newAdminButton.setObjectName("newAdminButton")
        self.adminButtonsHLayout.addWidget(self.newAdminButton)
        self.editAdminButton = QtWidgets.QPushButton(self.adminTab)
        font = QtGui.QFont()
        font.setPointSize(20)
        self.editAdminButton.setFont(font)
        self.editAdminButton.setObjectName("editAdminButton")
        self.adminButtonsHLayout.addWidget(self.editAdminButton)
        self.deleteAdminButton = QtWidgets.QPushButton(self.adminTab)
        font = QtGui.QFont()
        font.setPointSize(20)
        self.deleteAdminButton.setFont(font)
        self.deleteAdminButton.setObjectName("deleteAdminButton")
        self.adminButtonsHLayout.addWidget(self.deleteAdminButton)
        self.resetPinButton = QtWidgets.QPushButton(self.adminTab)
        font = QtGui.QFont()
        font.setPointSize(20)
        self.resetPinButton.setFont(font)
        self.resetPinButton.setObjectName("resetPinButton")
        self.adminButtonsHLayout.addWidget(self.resetPinButton)
        self.adminTableVLayout.addLayout(self.adminButtonsHLayout)
        self.adminTabHLayout.addLayout(self.adminTableVLayout)
        spacerItem4 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.adminTabHLayout.addItem(spacerItem4)
        self.adminTabHLayout.setStretch(0, 1)
        self.adminTabHLayout.setStretch(1, 1)
        self.tabWidget.addTab(self.adminTab, "")
        self.adminWindowVerticalLayout.addWidget(self.tabWidget)
        self.adminHorizontalLayout = QtWidgets.QHBoxLayout()
        self.adminHorizontalLayout.setSpacing(10)
        self.adminHorizontalLayout.setObjectName("adminHorizontalLayout")
        spacerItem5 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.adminHorizontalLayout.addItem(spacerItem5)
        self.closeButton = QtWidgets.QPushButton(AdminWindow)
        font = QtGui.QFont()
        font.setPointSize(20)
        self.closeButton.setFont(font)
        self.closeButton.setObjectName("closeButton")
        self.adminHorizontalLayout.addWidget(self.closeButton)
        spacerItem6 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.adminHorizontalLayout.addItem(spacerItem6)
        self.adminWindowVerticalLayout.addLayout(self.adminHorizontalLayout)

        self.retranslateUi(AdminWindow)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(AdminWindow)
        AdminWindow.setTabOrder(self.tabWidget, self.studentTable)
        AdminWindow.setTabOrder(self.studentTable, self.newStudentButton)
        AdminWindow.setTabOrder(self.newStudentButton, self.editStudentButton)
        AdminWindow.setTabOrder(self.editStudentButton, self.deleteStudentButton)
        AdminWindow.setTabOrder(self.deleteStudentButton, self.importStudentButton)
        AdminWindow.setTabOrder(self.importStudentButton, self.activityTable)
        AdminWindow.setTabOrder(self.activityTable, self.newActivityButton)
        AdminWindow.setTabOrder(self.newActivityButton, self.editActivityButton)
        AdminWindow.setTabOrder(self.editActivityButton, self.deleteActivityButton)
        AdminWindow.setTabOrder(self.deleteActivityButton, self.adminTable)
        AdminWindow.setTabOrder(self.adminTable, self.newAdminButton)
        AdminWindow.setTabOrder(self.newAdminButton, self.editAdminButton)
        AdminWindow.setTabOrder(self.editAdminButton, self.deleteAdminButton)
        AdminWindow.setTabOrder(self.deleteAdminButton, self.resetPinButton)
        AdminWindow.setTabOrder(self.resetPinButton, self.closeButton)

    def retranslateUi(self, AdminWindow):
        _translate = QtCore.QCoreApplication.translate
        AdminWindow.setWindowTitle(_translate("AdminWindow", "TimeTrack4237"))
        self.studentTableLabel.setText(_translate("AdminWindow", "Student Table"))
        self.newStudentButton.setText(_translate("AdminWindow", "New"))
        self.editStudentButton.setText(_translate("AdminWindow", "Edit"))
        self.deleteStudentButton.setText(_translate("AdminWindow", "Delete"))
        self.importStudentButton.setText(_translate("AdminWindow", "Import"))
        self.activityTableLabel.setText(_translate("AdminWindow", "Activity Table"))
        self.newActivityButton.setText(_translate("AdminWindow", "New"))
        self.editActivityButton.setText(_translate("AdminWindow", "Edit"))
        self.deleteActivityButton.setText(_translate("AdminWindow", "Delete"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tablesTab), _translate("AdminWindow", "Student / Activity"))
        self.adminTableLabel.setText(_translate("AdminWindow", "Admin Table"))
        self.newAdminButton.setText(_translate("AdminWindow", "New"))
        self.editAdminButton.setText(_translate("AdminWindow", "Edit"))
        self.deleteAdminButton.setText(_translate("AdminWindow", "Delete"))
        self.resetPinButton.setText(_translate("AdminWindow", "Reset PIN"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.adminTab), _translate("AdminWindow", "Admin"))
        self.closeButton.setText(_translate("AdminWindow", "Close"))