# coding:utf-8

__author__ =  'timmyliang'
__email__ =  '820472580@qq.com'
__date__ = '2020-01-04 20:42:11'

"""
设置断点脚本
"""
import sys
import time
from pdb import Pdb
from textwrap import dedent

import maya
from maya import cmds
from maya import mel

from Qt import QtGui
from Qt import QtCore
from Qt import QtWidgets

from .utils import mayaWindow
from .utils import mayaToQT
from .toolbar import Debugger_UI

class MPDB(Pdb,object):

    def __init__(self,widget):
        super(MPDB,self).__init__()
        self.widget = widget

    def interaction(self, frame, traceback):
        self.setup(frame, traceback)
        self.print_stack_entry(self.stack[self.curindex])
        # self.cmdloop()

        arg = self.widget.breakpoint(self)
        self.precmd(arg)
        self.onecmd(arg)

        self.forget()
        
    
def set_trace():
    MPDB_UI = "MPDB_DEBUGGER_UI"
    if not cmds.workspaceControl(MPDB_UI,q=1,ex=1):
        QtWidgets.QMessageBox.critical(mayaWindow(),u"错误",u"找不到 Debugger UI , 请尝试重装！")
        raise RuntimeError("Need to set up the Debugger UI!")
    elif not cmds.workspaceControl(MPDB_UI,q=1,vis=1):
        # NOTE 显示 Debugger
        cmds.workspaceControl(MPDB_UI,e=1,vis=1)
 
    MPDB_UI = mayaToQT(MPDB_UI).children()[-1]
    MPDB(MPDB_UI).set_trace(sys._getframe().f_back)

def install():
    import mpdb
    mpdb.debugger = Debugger_UI()
    mpdb.debugger_ui = mpdb.debugger.mayaShow()

# if __name__ == "__main__":
#     main()