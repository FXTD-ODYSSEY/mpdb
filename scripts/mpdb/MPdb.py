# coding:utf-8

__author__ =  'timmyliang'
__email__ =  '820472580@qq.com'
__date__ = '2020-01-04 20:42:11'

"""
设置断点脚本
"""
import sys
import time
import threading
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
        # NOTE 完成调试 跳过 Debug 模式
        if "<string>" == frame.f_code.co_filename:
            self.onecmd("c")
            self.forget()
            return

        self.print_stack_entry(self.stack[self.curindex])

        # self.cmdloop()
        stop = None
        while not stop:
            if self.cmdqueue:
                line = self.cmdqueue.pop(0)
            else:
                if self.use_rawinput:
                    line = self.widget.breakpoint(self,frame)
                else:
                    self.stdout.write(self.prompt)
                    self.stdout.flush()
                    line = self.stdin.readline()
                    if not len(line):
                        line = 'EOF'
                    else:
                        line = line.rstrip('\r\n')

            line = self.precmd(line)
            stop = self.onecmd(line)

        self.forget()
        
def loadDebugger():
    maya.utils.executeDeferred(dedent("""
        import mpdb
        import time
        curr = time.time()
        mpdb.debugger = mpdb.Debugger_UI()
        mpdb.debugger_ui = mpdb.debugger.mayaShow()
        elasped = time.time() - curr
        print elasped
    """))

def install():
    t  = threading.Thread(target=loadDebugger, args=())
    t.start()

def set_trace():
    MPDB_UI = "MPDB_DEBUGGER_UI"
    if not cmds.workspaceControl(MPDB_UI,q=1,ex=1):
        title = QtWidgets.QApplication.translate("error", "错误", None, -1)
        msg = QtWidgets.QApplication.translate("error", "找不到 Debugger UI , 请尝试重装！", None, -1)
        QtWidgets.QMessageBox.critical(mayaWindow(),title,msg)
        raise RuntimeError(msg)
    elif not cmds.workspaceControl(MPDB_UI,q=1,vis=1):
        # NOTE 显示 Debugger
        cmds.workspaceControl(MPDB_UI,e=1,vis=1)
 
    MPDB_UI = mayaToQT(MPDB_UI).children()[-1]
    MPDB(MPDB_UI).set_trace(sys._getframe().f_back)


# if __name__ == "__main__":
#     main()