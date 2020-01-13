# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'F:\repo\mpdb\scripts\mpdb\ui\debugVar.ui'
#
# Created: Mon Jan 13 21:09:23 2020
#      by: pyside2-uic  running on PySide2 2.0.0~alpha0
#
# WARNING! All changes made in this file will be lost!

from PySide2 import QtCore, QtGui, QtWidgets

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(408, 551)
        self.verticalLayout = QtWidgets.QVBoxLayout(Form)
        self.verticalLayout.setObjectName("verticalLayout")
        self.Var_Toggle = QtWidgets.QPushButton(Form)
        self.Var_Toggle.setObjectName("Var_Toggle")
        self.verticalLayout.addWidget(self.Var_Toggle)
        self.Var_Table = QtWidgets.QTableWidget(Form)
        self.Var_Table.setAutoScroll(True)
        self.Var_Table.setShowGrid(True)
        self.Var_Table.setGridStyle(QtCore.Qt.SolidLine)
        self.Var_Table.setCornerButtonEnabled(False)
        self.Var_Table.setObjectName("Var_Table")
        self.Var_Table.setColumnCount(2)
        self.Var_Table.setRowCount(2)
        item = QtWidgets.QTableWidgetItem()
        self.Var_Table.setVerticalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.Var_Table.setVerticalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.Var_Table.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.Var_Table.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.Var_Table.setItem(0, 0, item)
        item = QtWidgets.QTableWidgetItem()
        self.Var_Table.setItem(0, 1, item)
        item = QtWidgets.QTableWidgetItem()
        self.Var_Table.setItem(1, 0, item)
        item = QtWidgets.QTableWidgetItem()
        self.Var_Table.setItem(1, 1, item)
        self.Var_Table.horizontalHeader().setVisible(True)
        self.Var_Table.horizontalHeader().setCascadingSectionResizes(True)
        self.Var_Table.horizontalHeader().setSortIndicatorShown(False)
        self.Var_Table.horizontalHeader().setStretchLastSection(True)
        self.Var_Table.verticalHeader().setCascadingSectionResizes(False)
        self.Var_Table.verticalHeader().setHighlightSections(True)
        self.Var_Table.verticalHeader().setSortIndicatorShown(False)
        self.Var_Table.verticalHeader().setStretchLastSection(False)
        self.verticalLayout.addWidget(self.Var_Table)
        self.Scope_Toggle = QtWidgets.QPushButton(Form)
        self.Scope_Toggle.setObjectName("Scope_Toggle")
        self.verticalLayout.addWidget(self.Scope_Toggle)
        self.Scope_List = QtWidgets.QListWidget(Form)
        self.Scope_List.setObjectName("Scope_List")
        self.verticalLayout.addWidget(self.Scope_List)
        spacerItem = QtWidgets.QSpacerItem(20, 1, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        Form.setWindowTitle(QtWidgets.QApplication.translate("Form", "Form", None, -1))
        self.Var_Toggle.setText(QtWidgets.QApplication.translate("Form", "域变量", None, -1))
        self.Var_Table.setSortingEnabled(False)
        self.Var_Table.verticalHeaderItem(0).setText(QtWidgets.QApplication.translate("Form", "1", None, -1))
        self.Var_Table.verticalHeaderItem(1).setText(QtWidgets.QApplication.translate("Form", "2", None, -1))
        self.Var_Table.horizontalHeaderItem(0).setText(QtWidgets.QApplication.translate("Form", "变量名", None, -1))
        self.Var_Table.horizontalHeaderItem(1).setText(QtWidgets.QApplication.translate("Form", "变量值", None, -1))
        __sortingEnabled = self.Var_Table.isSortingEnabled()
        self.Var_Table.setSortingEnabled(False)
        self.Var_Table.item(0, 0).setText(QtWidgets.QApplication.translate("Form", "a", None, -1))
        self.Var_Table.item(0, 1).setText(QtWidgets.QApplication.translate("Form", "1", None, -1))
        self.Var_Table.item(1, 0).setText(QtWidgets.QApplication.translate("Form", "b", None, -1))
        self.Var_Table.item(1, 1).setText(QtWidgets.QApplication.translate("Form", "2", None, -1))
        self.Var_Table.setSortingEnabled(__sortingEnabled)
        self.Scope_Toggle.setText(QtWidgets.QApplication.translate("Form", "函数域", None, -1))

