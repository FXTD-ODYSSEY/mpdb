# coding:utf-8

__author__ =  'timmyliang'
__email__ =  '820472580@qq.com'
__date__ = '2020-01-04 20:42:11'

"""
设置断点脚本
"""
import os
import sys
from pdb import Pdb
from bdb import BdbQuit
from functools import wraps

import maya
from maya import cmds

from Qt import QtGui
from Qt import QtCore
from Qt import QtWidgets

from .utils import mayaWindow
from .toolbar import Debugger_UI

def debugMode(func):
    """debugMode Debug 装饰器
    """
    @wraps(func)
    def wrapper(self,*args, **kwargs):
        
        args = func(self,*args, **kwargs)
        self.forget()
        self.clearPanel()
        return args
    return wrapper


def get_stack(f):
    stack = []
    print "================",[f]
    while f is not None:
        stack.append(f)
        filename = f.f_code.co_filename
        lineno = f.f_lineno
        print "file",filename,lineno
        f = f.f_back
    return stack 

def ignoreBdbQuitError(func):
    """debugMode 过滤 BdbQuit 装饰器
    """
    @wraps(func)
    def wrapper(self, frame):
        try:
            return func(self, frame)
        except BdbQuit:
            # get_stack(frame) 
            # NOTE https://stackoverflow.com/questions/19782075/how-to-stop-terminate-a-python-script-from-running
            sys.exit()
    return wrapper

class MPDB(Pdb,object):

    def __init__(self,widget):
        super(MPDB,self).__init__()
        self.widget = widget
        DIR = os.path.dirname(__file__)
        self.py_list = [filename for filename in os.listdir(DIR) if filename.endswith(".py")]
        
    @debugMode
    def interaction(self, frame, traceback):
        self.setup(frame, traceback)
        # NOTE 完成调试 跳过 Debug 模式
        stack_list = self.stack if int(cmds.about(v=1)) > 2017 else self.stack[2:]
        if not stack_list or "__exception__" in frame.f_locals:
            self.onecmd("c")
            return
        
        # NOTE 过滤插件自身的 代码追踪
        filename = self.curframe.f_code.co_filename.strip()
        for py in self.py_list:
            if r"mpdb" in filename and py in filename:
                self.onecmd("u")
                self.onecmd("c")
                return

        self.print_stack_entry(self.stack[self.curindex])

        self.updatePanel()
        # self.cmdloop()
        stop = None
        while not stop:
            if self.cmdqueue:
                line = self.cmdqueue.pop(0)
            else:
                line = self.widget.breakpoint(self,frame)
      
            line = self.precmd(line)
            stop = self.onecmd(line)

    
    def clearPanel(self):
        # NOTE 清空面板数据
        panel = self.widget.panel
        panel.link.setText("")
        panel.editor.setPlainText("")
        panel.info_panel.clear()
        panel.info_panel.Scope_List.clear()

    def updatePanel(self,f_locals=None):
        filename = self.curframe.f_code.co_filename
        lineno = self.curframe.f_lineno
        var_data = f_locals if f_locals else self.curframe_locals

        # NOTE 代码显示
        if os.path.exists(filename):
            try:
                with open(filename,'r') as f:
                    code = f.read()
            except:
                code = "%s %s" % (filename , QtWidgets.QApplication.translate("reading", "read fail"))
        else:
            code = "%s %s" % (filename , QtWidgets.QApplication.translate("reading", "file not exists"))
        
        # NOTE 更新路径和代码
        panel = self.widget.panel
        panel.link.setText(filename,lineno)
        panel.editor.setPlainText(code)
        panel.editor.paintLine(lineno)
        panel.info_panel.clear()
        panel.info_panel.addItems(var_data)
        
        # NOTE 更新函数域
        Scope_List = panel.info_panel.Scope_List
        Scope_List.clear()
        
        stack_list = self.stack if int(cmds.about(v=1)) > 2017 else self.stack[2:]
        for stack,lineno in stack_list:
            filename = stack.f_code.co_filename
            item = QtWidgets.QListWidgetItem("%s(%s)" % (filename,lineno))
            item.frame = stack
            item.locals = stack.f_locals
            item.globals = stack.f_globals
            Scope_List.addItem(item)

        # NOTE 选择当前函数域最后的 item
        if stack_list:
            Scope_List.setCurrentItem(item)

    def default(self, line):
        if line[:1] == '!': line = line[1:]
        locals = self.curframe_locals
        globals = self.curframe.f_globals
        try:
            code = compile(line + '\n', '<stdin>', 'single')
            save_stdout = sys.stdout
            save_stdin = sys.stdin
            save_displayhook = sys.displayhook
            try:
                sys.stdin = self.stdin
                sys.stdout = self.stdout
                sys.displayhook = self.displayhook
                exec code in globals, locals
            finally:
                sys.stdout = save_stdout
                sys.stdin = save_stdin
                sys.displayhook = save_displayhook
        except:
            t, v = sys.exc_info()[:2]
            if type(t) == type(''):
                exc_type_name = t
            else: exc_type_name = t.__name__
            print >>self.stdout, '***', exc_type_name + ':', v
        
        # NOTE pdb输入修改 更新面板
        self.updatePanel(locals)
    
    def do_quitIgnore(self, arg):
        self._user_requested_quit = 1
        self.set_quit()
        return 1

    @ignoreBdbQuitError
    def dispatch_line(self, frame):
        return super(MPDB,self).dispatch_line(frame)

    # @ignoreBdbQuitError
    # def trace_dispatch(self, frame, event, arg):
    #     return super(MPDB,self).trace_dispatch(frame, event, arg)

def install():
    import mpdb
    MPDB_UI = Debugger_UI.windowName
    if not cmds.workspaceControl(MPDB_UI,q=1,ex=1):
        mpdb.debugger = mpdb.Debugger_UI()
        mpdb.debugger_ui = mpdb.debugger.mayaShow()
    elif not hasattr(mpdb,"debugger"):
        cmds.deleteUI(MPDB_UI)
        mpdb.debugger = mpdb.Debugger_UI()
        mpdb.debugger_ui = mpdb.debugger.mayaShow()
    else:
        title = QtWidgets.QApplication.translate("warn", "warning")
        msg = QtWidgets.QApplication.translate("warn", "Debugger UI already install")
        QtWidgets.QMessageBox.warning(mayaWindow(),title,msg)

def set_trace():
    import mpdb
    # NOTE 过滤 退出状态 和 Debug 状态
    if mpdb.quitting or mpdb.debugger.debug_icon.isEnabled():
        return

    MPDB_UI = Debugger_UI.windowName
    if not hasattr(mpdb,"debugger") or not cmds.workspaceControl(MPDB_UI,q=1,ex=1):
        title = QtWidgets.QApplication.translate("error", "error")
        msg = QtWidgets.QApplication.translate("error", "Connot find Debugger UI,Please try to reinstall the plugin")
        QtWidgets.QMessageBox.critical(mayaWindow(),title,msg)
        raise RuntimeError(msg)
    elif not cmds.workspaceControl(MPDB_UI,q=1,vis=1):
        # NOTE 显示 Debugger
        cmds.workspaceControl(MPDB_UI,e=1,vis=1)
    
    # NOTE 设置断点
    MPDB(mpdb.debugger).set_trace(sys._getframe().f_back)

