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
from functools import partial
from functools import wraps
import toolbar_rc

from .utils import createUIComponentToolBar
from .utils import mayaWindow
from .utils import getStatusLine
from .utils import traverseChildren
from .utils import mayaToQT

from .scriptEditor import enhanceScriptEditor

from PySide2 import QtGui
from PySide2 import QtCore
from PySide2 import QtWidgets
from Qt.QtCompat import loadUi
from Qt.QtCompat import wrapInstance


import maya
from maya import cmds
from maya import mel
from maya import OpenMayaUI

from .panel import Debugger_Panel

DIR = os.path.dirname(__file__)

class OverLay(QtWidgets.QWidget):
    BorderColor     = QtGui.QColor(255, 0, 0, 255)     
    BackgroundColor = QtGui.QColor(255, 255, 255, 0) 
    
    def __init__(self, *args, **kwargs):
        QtWidgets.QWidget.__init__(self, *args, **kwargs)
        self.setAttribute(QtCore.Qt.WA_NoSystemBackground)
        self.setAttribute(QtCore.Qt.WA_TransparentForMouseEvents)
        self.setWindowFlags(QtCore.Qt.WindowTransparentForInput|QtCore.Qt.FramelessWindowHint)
        self.setFocusPolicy( QtCore.Qt.NoFocus )
        self.hide()
        # self.setEnabled(False)

        self.setAutoFillBackground(True)
        # self.setWindowFlags(QtCore.Qt.FramelessWindowHint)

    def paintEvent(self, event):
        
        # NOTE https://stackoverflow.com/questions/51687692/how-to-paint-roundedrect-border-outline-the-same-width-all-around-in-pyqt-pysi
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)   

        rectPath = QtGui.QPainterPath()                      
        height = self.height() - 4                     
        rect = QtCore.QRectF(2, 2, self.width()-4, height)
        rectPath.addRoundedRect(rect, 15, 15)
        painter.setPen(QtGui.QPen(self.BorderColor, 2, QtCore.Qt.SolidLine,QtCore.Qt.RoundCap, QtCore.Qt.RoundJoin))
        painter.drawPath(rectPath)
        painter.setBrush(self.BackgroundColor)
        painter.drawRoundedRect(rect, 15, 15)

def setDebugIcon(func):
    @wraps(func)
    def wrapper(self,*args, **kwargs):
        main_win = mayaWindow()
        main_win.setStyleSheet("#MayaWindow {background:red}")
        self.debug_icon.setEnabled(True)
        args = func(self,*args, **kwargs)
        self.debug_icon.setEnabled(False)
        main_win.setStyleSheet("")
        return args

    return wrapper
    
class Debugger_UI(QtWidgets.QWidget):
    def __init__(self):
        super(Debugger_UI,self).__init__()

        ui_path = os.path.join(DIR,"ui","debug.ui")
        loadUi(ui_path,self)
        
        self.debug_continue_state  = False
        self.debug_step_over_state = False
        self.debug_step_into_state = False
        self.debug_step_out_state  = False
        self.debug_cancel_state    = False

        self.setButtonColor(self.debug_continue,QtGui.QColor(117, 190, 255))
        self.setButtonColor(self.debug_step_over,QtGui.QColor(117, 190, 255))
        self.setButtonColor(self.debug_step_into,QtGui.QColor(117, 190, 255))
        self.setButtonColor(self.debug_step_out,QtGui.QColor(117, 190, 255))
        self.setButtonColor(self.debug_cancel)
        self.setButtonColor(self.debug_setting,QtGui.QColor(215, 215, 215))

        self.debug_icon.setEnabled(False)
        self.debug_continue.clicked.connect(partial(self.setContinue,True))
        self.debug_step_over.clicked.connect(partial(self.setStep_over,True))
        self.debug_step_into.clicked.connect(partial(self.setStep_into,True))
        self.debug_step_out.clicked.connect(partial(self.setStep_out,True))
        self.debug_cancel.clicked.connect(partial(self.setCancel,True))
        self.debug_setting.clicked.connect(self.openPanel)

        cmdWndIcon = self.setUpScriptIcon()
        enhanceScriptEditor()
        
    #     self.main_win = mayaWindow()
    #     self.main_win.installEventFilter(self)

    # def eventFilter(self,reciever, event):
    #     # NOTE 添加 Ctrl + E 作为执行快捷键
    #     if event.type() == QtCore.QEvent.Type.KeyPress:
    #         print "===================="
    #         active_win = QtWidgets.QApplication.activeWindow()
    #         print active_win.objectName()
        

    def deleteEvent(self):
        # self.main_win.removeEventFilter(self)
        cmds.deleteUI("MPDB_DEBUGGER_UI")
        self.deleteLater()

    def setUpScriptIcon(self):
        # get command line formLayout
        gCommandLineForm = mel.eval('$tempVar = $gCommandLineForm')
        commandLineForm = cmds.formLayout(gCommandLineForm, q=1, ca=1)[0]
        # get cmdWndIcon button
        cmdWndIcon = cmds.formLayout(commandLineForm, q=1, ca=1)[-1]
        # change the command of the button
        menu_list = cmds.symbolButton(cmdWndIcon, q=1, popupMenuArray=1)
        if menu_list:
            cmds.deleteUI(menu_list)

        # Note 添加右键菜单打开
        # TODO 使用中键打开
        cmds.popupMenu(p=cmdWndIcon)
        cmds.menuItem(l=u"Open Debugger",c=lambda x: cmds.evalDeferred(Debugger_UI().mayaShow))

        return cmdWndIcon
        
    def setContinue(self,state):
        self.debug_continue_state  = state

    def setStep_over(self,state):
        self.debug_step_over_state = state

    def setStep_into(self,state):
        self.debug_step_into_state = state

    def setStep_out(self,state):
        self.debug_step_out_state  = state

    def setCancel(self,state):
        self.debug_cancel_state    = state

    def openPanel(self):
        self.panel = Debugger_Panel().mayaShow()
        
    # def startDebugMode(self,state):
    #     self.debugMode = state
    #     main_win = mayaWindow()
    #     if state:
    #         main_win.setStyleSheet("#MayaWindow {background:red}")
    #     else:
    #         main_win.setStyleSheet("")
        

    def setButtonColor(self,button,color=QtGui.QColor("red"),size=25):
        icon = button.icon()
        pixmap = icon.pixmap(size)
        image = pixmap.toImage()
        pcolor = image.pixelColor(size,size)
        for x in range(image.width()):
            for y in range(image.height()):
                pcolor = image.pixelColor(x, y)
                if pcolor.alpha() > 0:
                    color.setAlpha(pcolor.alpha())
                    image.setPixelColor(x, y, color)
        button.setIcon(QtGui.QIcon(QtGui.QPixmap.fromImage(image)))
        
    @setDebugIcon
    def breakpoint(self,MPDB,frame):
        curr = time.time()

        while True:
            elapsed = abs(curr - time.time())
            # print elapsed
            
            if elapsed > 3:
                print "run out of time"
                return "q"

            if self.debug_continue_state  :
                self.debug_continue_state  = False
                return "c"

            if self.debug_step_over_state :
                self.debug_step_over_state = False
                return "n"

            if self.debug_step_into_state :
                self.debug_step_into_state = False
                return "s"

            if self.debug_step_out_state  :
                self.debug_step_out_state  = False
                return "u;;n"

            if self.debug_cancel_state    :
                self.debug_cancel_state    = False
                return "q"

            # NOTE Keep Maya alive 
            QtCore.QCoreApplication.processEvents()
            maya.utils.processIdleEvents()
    
    def mayaShow(self,name=u"MPDB_DEBUGGER_UI"):
        
        if not cmds.workspaceControl(name,ex=1):
            
            toolBar = createUIComponentToolBar(name)
            cmds.workspaceControl(name,e=1,r=1)
            toolBar.layout().addWidget(self)
            # toolBar.setFixedHeight(0)
            # toolBar.setMaximumWidth(self.maximumWidth())
            # toolBar.setMaximumHeight(self.maximumHeight())

            # NOTE tab widget to the command Line
            cmds.workspaceControl(name,e=1,
                dockToControl=["CommandLine","right"],
            )
            
            return toolBar
        else:
            if not cmds.workspaceControl(name,q=1,vis=1):
                cmds.workspaceControl(name,e=1,vis=1)
            if cmds.workspaceControl(name,q=1,fl=1):
                cmds.evalDeferred(dedent("""
                    from maya import cmds
                    cmds.workspaceControl('%s',e=1,
                        dockToControl=["CommandLine","right"],
                        loadImmediately= 1
                    )
                """ % name))

# import sys
# MODULE = r"D:\Users\82047\Desktop\repo\mpdb\scripts"
# if MODULE not in sys.path:
#     sys.path.append(MODULE)

# try:
        
#     import mpdb
#     reload(mpdb)

#     debugger = mpdb.Debugger_UI()
#     debugger_ui = debugger.mayaShow()
# except:
#     import traceback
#     traceback.print_exc()
# # debugger.deleteEvent()


# import sys
# MODULE = r"D:\Users\82047\Desktop\repo\mpdb\scripts"
# if MODULE not in sys.path:
#     sys.path.append(MODULE)

# try:
        
#     import mpdb
#     reload(mpdb)

#     mpdb.install()
    
# except:
#     import traceback
#     traceback.print_exc()
# # mpdb.debugger.deleteEvent()