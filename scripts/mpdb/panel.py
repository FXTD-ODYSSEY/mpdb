# coding:utf-8

__author__ =  'timmyliang'
__email__ =  '820472580@qq.com'
__date__ = '2020-01-05 22:10:22'

"""
Debugger UI setup
"""
import os
import sys
import time
from textwrap import dedent

import toolbar_rc

from .utils import createUIComponentToolBar
from .utils import mayaWindow
from .utils import CollapsibleWidget
from .utils import mayaShow

from PySide2 import QtGui
from PySide2 import QtCore
from PySide2 import QtWidgets
from Qt.QtCompat import loadUi
from Qt.QtCompat import wrapInstance

from maya import cmds
from maya import mel
from maya import OpenMayaUI


DIR = os.path.dirname(__file__)

class Debugger_Panel(QtWidgets.QWidget):
    def __init__(self):
        super(Debugger_Panel,self).__init__()

        ui_path = os.path.join(DIR,"ui","debugVar.ui")
        loadUi(ui_path,self)
        
        self.var_toggle_anim = CollapsibleWidget.install(self.Var_Toggle,self.Var_Table)
        self.scope_toggle_anim = CollapsibleWidget.install(self.Scope_Toggle,self.Scope_List)

        print self.Var_Table
        print dir(self.Var_Table)

    # def createTable(self):
    #    # Create table
    #     self.tableWidget = QTableWidget()
    #     self.tableWidget.setRowCount(4)
    #     self.tableWidget.setColumnCount(2)
    #     self.tableWidget.setItem(0,0, QTableWidgetItem("Cell (1,1)"))
    #     self.tableWidget.setItem(0,1, QTableWidgetItem("Cell (1,2)"))
    #     self.tableWidget.setItem(1,0, QTableWidgetItem("Cell (2,1)"))
    #     self.tableWidget.setItem(1,1, QTableWidgetItem("Cell (2,2)"))
    #     self.tableWidget.setItem(2,0, QTableWidgetItem("Cell (3,1)"))
    #     self.tableWidget.setItem(2,1, QTableWidgetItem("Cell (3,2)"))
    #     self.tableWidget.setItem(3,0, QTableWidgetItem("Cell (4,1)"))
    #     self.tableWidget.setItem(3,1, QTableWidgetItem("Cell (4,2)"))
    #     self.tableWidget.move(0,0)
    #     # table selection change
    #     self.tableWidget.doubleClicked.connect(self.on_click)

    

    def mayaShow(self):
        return mayaShow(self,"MPDB_Panel")

# import sys
# MODULE = r"F:\repo\mpdb\scripts"
# if MODULE not in sys.path:
#     sys.path.append(MODULE)

# try:
        
#     import mpdb
#     reload(mpdb)

#     debugger_ui = mpdb.Debugger_Panel().mayaShow()
# except:
#     import traceback
#     traceback.print_exc()