# coding:utf-8

__author__ =  'timmyliang'
__email__ =  '820472580@qq.com'
__date__ = '2020-01-04 20:42:11'

"""
设置断点脚本
"""
import os
import sys
import threading
from pdb import Pdb
from bdb import BdbQuit
from functools import wraps
from textwrap import dedent

import maya
from maya import cmds

from Qt import QtGui
from Qt import QtCore
from Qt import QtWidgets

from .utils import mayaWindow
from .toolbar import Debugger_UI
from .scriptEditor import enhanceScriptEditor

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
        self.py_list = [os.path.join(DIR,filename) for filename in os.listdir(DIR) if filename.endswith(".py")]
    
    def clearPanel(self):
        # NOTE 清空面板数据
        self.widget.panel.clear()

    def updatePanel(self,f_locals=None):
        self.widget.panel.updatePanel(self,f_locals)
         
    @debugMode
    def interaction(self, frame, traceback):
        self.setup(frame, traceback)
        # NOTE 完成调试 跳过 Debug 模式
        stack_list = self.stack if int(cmds.about(v=1)) > 2017 else self.stack[2:]
        if not stack_list or "__exception__" in frame.f_locals:
            self.onecmd("c")
            return
        
        filename = os.path.realpath(self.curframe.f_code.co_filename)
        # NOTE 过滤 Python 官方库 的 代码追踪
        if "python27.zip" in filename:
            self.onecmd("u")
            self.onecmd("n")
            return

        # NOTE 过滤插件自身的 代码追踪
        for py in self.py_list:
            if os.path.realpath(py) == filename:
                self.onecmd("u")
                self.onecmd("n")
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

def __setupUi():
    import mpdb
    mpdb.debugger.initialize()
    # QtWidgets.QApplication.processEvents()
    cmds.evalDeferred(dedent("""
        import mpdb
        mpdb.debugger_ui = mpdb.debugger.mayaShow()
    """))

def install():
    import mpdb
    MPDB_UI = Debugger_UI.windowName
    if not hasattr(mpdb,"debugger") and cmds.workspaceControl(MPDB_UI,q=1,ex=1):
        cmds.deleteUI(MPDB_UI)
    
    if not cmds.workspaceControl(MPDB_UI,q=1,ex=1):
        enhanceScriptEditor()
        mpdb.debugger = mpdb.Debugger_UI()
        # mpdb.debugger.initialize()
        # mpdb.debugger_ui = mpdb.debugger.mayaShow()
        thread = threading.Thread(target=__setupUi)
        thread.start()
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

