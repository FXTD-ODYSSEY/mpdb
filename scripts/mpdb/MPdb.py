# coding:utf-8

__author__ =  'timmyliang'
__email__ =  '820472580@qq.com'
__date__ = '2020-01-04 20:42:11'

"""
设置断点脚本
"""
import sys
from pdb import Pdb
import time

import maya
from maya import cmds
from maya import mel

from Qt import QtGui
from Qt import QtCore
from Qt import QtWidgets

from PySide2 import QtGui
from PySide2 import QtCore
from PySide2 import QtWidgets

from utils import mayaWindow

class MPdb(Pdb,object):

    def __init__(self,widget):
        super(MPdb.self).__init__()
        self.widget = widget

    def interaction(self, frame, traceback):
        self.setup(frame, traceback)
        self.print_stack_entry(self.stack[self.curindex])
        # self.cmdloop()
        arg = self.getProcess()
        self.precmd(arg)
        self.onecmd(arg)

        self.forget()
        
    def getProcess(self):
        curr = time.time()

        while True:
            
            if abs(curr - time.time()) < 3:
                break

            QtCore.QCoreApplication.processEvents()
            maya.utils.processIdleEvents()
            

def set_trace():
    global MPDB_UI
    if not MPDB_UI:
        QtWidgets.QMessageBox.critical(mayaWindow(),u"错误",u"找不到调试器UI , 请尝试重装！")
        raise RuntimeError("Need to set up the Debugger UI!")
    MPdb(MPDB_UI).set_trace(sys._getframe().f_back)

# if __name__ == "__main__":
#     main()