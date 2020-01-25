# coding:utf-8

__author__ =  'timmyliang'
__email__ =  '820472580@qq.com'
__date__ = '2020-01-04 20:42:11'

"""
设置断点脚本
"""
import os
import sys
import time
import threading
from pdb import Pdb
from bdb import BdbQuit
from textwrap import dedent
from functools import wraps

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

        self.updatePanel()
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
        self.clearPanel()
    
    def clearPanel(self):
        # NOTE 清空面板数据
        panel = self.widget.panel
        panel.link.setText("")
        panel.editor.setPlainText("")
        panel.info_panel.clear()
        panel.info_panel.Scope_List.clear()

    def updatePanel(self):
        filename = self.curframe.f_code.co_filename
        lineno = self.curframe.f_lineno
        var_data = self.curframe.f_locals
        panel = self.widget.panel

        if os.path.exists(filename):
            with open(filename,'r') as f:
                code = f.read()
        else:
            code = ""
        
        # NOTE 更新路径和代码
        panel.link.setText(filename,lineno)
        panel.editor.setPlainText(code)
        panel.editor.paintLine(lineno)
        panel.info_panel.clear()
        panel.info_panel.addItems(var_data)

        Scope_List = panel.info_panel.Scope_List
        Scope_List.clear()
        
        stack_list = self.stack if int(cmds.about(v=1)) > 2017 else self.stack[2:]
        for stack,lineno in stack_list:
            filename = stack.f_code.co_filename
            item = QtWidgets.QListWidgetItem("%s(%s)" % (filename,lineno))
            item.locals = stack.f_locals
            panel.info_panel.Scope_List.addItem(item)
            
def install():
    import mpdb
    MPDB_UI = Debugger_UI.windowName
    if not cmds.workspaceControl(MPDB_UI,q=1,ex=1):
        mpdb.debugger = mpdb.Debugger_UI()
        mpdb.debugger_ui = mpdb.debugger.mayaShow()
    else:
        title = QtWidgets.QApplication.translate("warn", "warning")
        msg = QtWidgets.QApplication.translate("warn", "Debugger UI already install")
        QtWidgets.QMessageBox.warning(mayaWindow(),title,msg)

    
def set_trace():
    import mpdb
    MPDB_UI = Debugger_UI.windowName
    if not hasattr(mpdb,"debugger") or not cmds.workspaceControl(MPDB_UI,q=1,ex=1):
        title = QtWidgets.QApplication.translate("error", "error")
        msg = QtWidgets.QApplication.translate("error", "Connot find Debugger UI,Please try to reinstall the plugin")
        QtWidgets.QMessageBox.critical(mayaWindow(),title,msg)
        raise RuntimeError(msg)
    elif not cmds.workspaceControl(MPDB_UI,q=1,vis=1):
        # NOTE 显示 Debugger
        cmds.workspaceControl(MPDB_UI,e=1,vis=1)
 
    # debugger = mayaToQT(MPDB_UI).children()[-1]
    MPDB(mpdb.debugger).set_trace(sys._getframe().f_back)

