# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'D:\Users\82047\Desktop\repo\mpdb\scripts\mpdb\icon\debug.ui'
#
# Created by: PyQt5 UI code generator 5.6
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(240, 50)
        Form.setMaximumSize(QtCore.QSize(300, 50))
        self.horizontalLayout = QtWidgets.QHBoxLayout(Form)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.debug_continue = QtWidgets.QToolButton(Form)
        self.debug_continue.setMaximumSize(QtCore.QSize(32, 32))
        self.debug_continue.setStyleSheet("")
        self.debug_continue.setText("")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/debug/debug_continue.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.debug_continue.setIcon(icon)
        self.debug_continue.setIconSize(QtCore.QSize(32, 32))
        self.debug_continue.setAutoRaise(True)
        self.debug_continue.setObjectName("debug_continue")
        self.horizontalLayout.addWidget(self.debug_continue)
        self.debug_step_over = QtWidgets.QToolButton(Form)
        self.debug_step_over.setMaximumSize(QtCore.QSize(32, 32))
        self.debug_step_over.setStyleSheet("")
        self.debug_step_over.setText("")
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(":/debug/debug_step_over.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.debug_step_over.setIcon(icon1)
        self.debug_step_over.setIconSize(QtCore.QSize(32, 32))
        self.debug_step_over.setAutoRaise(True)
        self.debug_step_over.setObjectName("debug_step_over")
        self.horizontalLayout.addWidget(self.debug_step_over)
        self.debug_step_into = QtWidgets.QToolButton(Form)
        self.debug_step_into.setMaximumSize(QtCore.QSize(32, 32))
        self.debug_step_into.setStyleSheet("")
        self.debug_step_into.setText("")
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap(":/debug/debug_step_into.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.debug_step_into.setIcon(icon2)
        self.debug_step_into.setIconSize(QtCore.QSize(32, 32))
        self.debug_step_into.setAutoRaise(True)
        self.debug_step_into.setObjectName("debug_step_into")
        self.horizontalLayout.addWidget(self.debug_step_into)
        self.debug_step_out = QtWidgets.QToolButton(Form)
        self.debug_step_out.setMaximumSize(QtCore.QSize(32, 32))
        self.debug_step_out.setStyleSheet("")
        self.debug_step_out.setText("")
        icon3 = QtGui.QIcon()
        icon3.addPixmap(QtGui.QPixmap(":/debug/debug_step_out.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.debug_step_out.setIcon(icon3)
        self.debug_step_out.setIconSize(QtCore.QSize(32, 32))
        self.debug_step_out.setAutoRaise(True)
        self.debug_step_out.setObjectName("debug_step_out")
        self.horizontalLayout.addWidget(self.debug_step_out)
        self.debug_cancel = QtWidgets.QToolButton(Form)
        self.debug_cancel.setMaximumSize(QtCore.QSize(32, 32))
        self.debug_cancel.setStyleSheet("")
        self.debug_cancel.setText("")
        icon4 = QtGui.QIcon()
        icon4.addPixmap(QtGui.QPixmap(":/debug/debug_cancel.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.debug_cancel.setIcon(icon4)
        self.debug_cancel.setIconSize(QtCore.QSize(32, 32))
        self.debug_cancel.setAutoRaise(True)
        self.debug_cancel.setObjectName("debug_cancel")
        self.horizontalLayout.addWidget(self.debug_cancel)
        self.debug_setting = QtWidgets.QToolButton(Form)
        self.debug_setting.setMaximumSize(QtCore.QSize(32, 32))
        self.debug_setting.setStyleSheet("")
        self.debug_setting.setText("")
        icon5 = QtGui.QIcon()
        icon5.addPixmap(QtGui.QPixmap(":/debug/debug_setting.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.debug_setting.setIcon(icon5)
        self.debug_setting.setIconSize(QtCore.QSize(32, 32))
        self.debug_setting.setAutoRaise(True)
        self.debug_setting.setObjectName("debug_setting")
        self.horizontalLayout.addWidget(self.debug_setting)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "mpdb Debugger"))

import debug_rc
