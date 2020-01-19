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
from .utils import getStatusLine
from .utils import traverseChildren
from .utils import mayaToQT

from PySide2 import QtGui
from PySide2 import QtCore
from PySide2 import QtWidgets
from Qt.QtCompat import loadUi
from Qt.QtCompat import wrapInstance

from maya import cmds
from maya import mel
from maya import OpenMayaUI

from .panel import Debugger_Panel

DIR = os.path.dirname(__file__)


# class Filter(QtCore.QObject):
#     def __init__(self, *args, **kwargs):
#         QtCore.QObject.__init__(self, *args, **kwargs)
#         self.m_overlay = None
#         self.m_overlayOn = None

#     def eventFilter(self, obj, event):
#         if not obj.isWidgetType():
#             return False
#         if event.type() == QtCore.QEvent.MouseButtonPress:
#             if not self.m_overlay:
#                 self.m_overlay = OverLay(obj.parentWidget())
#             self.m_overlay.setGeometry(obj.geometry())
#             self.m_overlayOn = obj
#             self.m_overlay.show()
#         elif event.type() == QtCore.QEvent.Resize:
#             if self.m_overlay and self.m_overlayOn == obj:
#                 self.m_overlay.setGeometry(obj.geometry())
#         return False

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
        self.setEnabled(False)

        # self.setAutoFillBackground(True)
        # self.setWindowFlags(QtCore.Qt.FramelessWindowHint)

    def paintEvent(self, event):
        
        # NOTE https://stackoverflow.com/questions/51687692/how-to-paint-roundedrect-border-outline-the-same-width-all-around-in-pyqt-pysi
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)   

        rectPath = QtGui.QPainterPath()                      
        height = self.height() - 4                     
        rectPath.addRoundedRect(QtCore.QRectF(2, 2, self.width()-4, height), 15, 15)
        painter.setPen(QtGui.QPen(self.BorderColor, 2, QtCore.Qt.SolidLine,QtCore.Qt.RoundCap, QtCore.Qt.RoundJoin))
        painter.drawPath(rectPath)
        painter.setBrush(self.BackgroundColor)

class Debugger_UI(QtWidgets.QWidget):
    def __init__(self):
        super(Debugger_UI,self).__init__()

        ui_path = os.path.join(DIR,"ui","debug.ui")
        loadUi(ui_path,self)


        self.setButtonColor(self.debug_continue,QtGui.QColor(117, 190, 255))
        self.setButtonColor(self.debug_step_over,QtGui.QColor(117, 190, 255))
        self.setButtonColor(self.debug_step_into,QtGui.QColor(117, 190, 255))
        self.setButtonColor(self.debug_step_out,QtGui.QColor(117, 190, 255))
        self.setButtonColor(self.debug_cancel)
        self.setButtonColor(self.debug_setting,QtGui.QColor(215, 215, 215))

        self.debug_icon.setEnabled(False)
        # self.debug_setting.clicked.connect(self.openPanel)
        self.debug_setting.clicked.connect(self.startDebugMode)

        self.setUpScriptBar()

        # window = mayaWindow()
        # self.border = QtWidgets.QWidget()
        # self.border.setParent(window)
        # self.border.setMinimumSize(400,400)
        # self.border.setStyleSheet("border: 5px solid red;background:black;")
        # self.border.show()
        # window.installEventFilter(self)
        # self.setStyleSheet("border: 5px solid red;background:black;")

        self.m_overlay = None
        self.debugMode = False
        main_win = mayaWindow()


        workspace = mel.eval("$temp = $gWorkAreaForm")
        workspace = mayaToQT(workspace)

        # print workspace.children()

        flag = 0
        for widget in workspace.children():
            if type(widget) == QtWidgets.QSplitter:
                break

        
                
        print widget,widget.children(),widget.objectName()
        # for _widget in widget.children():
        #     if type(_widget) == QtWidgets.QWidget:
        #         break

        # print widget,flag,widget.objectName()
        self.m_overlay = OverLay(widget)
        widget.installEventFilter(self)


    def deleteEvent(self):
        if self.m_overlay:
            self.m_overlay.setParent(None)
        cmds.deleteUI("MPDB_DEBUGGER_UI")

    def eventFilter(self, obj, event):
        if not obj.isWidgetType():
            return False
        
        if self.debugMode:
            self.m_overlay.setGeometry(QtCore.QRect(0,0,obj.width(),obj.height()))
        elif event.type() == QtCore.QEvent.Resize:
            self.m_overlay.setGeometry(QtCore.QRect(0,0,obj.width(),obj.height()))
        return False


    def setUpScriptBar(self):
        # get command line formLayout
        gCommandLineForm = mel.eval('$tempVar = $gCommandLineForm')
        commandLineForm = cmds.formLayout(gCommandLineForm, q=1, ca=1)[0]
        # get cmdWndIcon button
        cmdWndIcon = cmds.formLayout(commandLineForm, q=1, ca=1)[-1]
        # change the command of the button
        menu_list = cmds.symbolButton(cmdWndIcon, q=1, popupMenuArray=1)
        if menu_list:
            cmds.deleteUI(menu_list)

        cmds.popupMenu(p=cmdWndIcon)
        cmds.menuItem(l=u"Open Debugger",c=lambda x: cmds.evalDeferred(Debugger_UI().mayaShow))

    def rightClickMenu(self, event):
        self.menu = QtWidgets.QMenu(self)
        goto_action = QtWidgets.QAction('Goto Line', self)

        goto_action.triggered.connect(self.gotoLine)
        self.menu.addAction(goto_action)
        pos = QtGui.QCursor.pos()
        self.menu.popup(pos)
        

    def openPanel(self):
        self.panel = Debugger_Panel()
        self.panel.mayaShow()
        
    def startDebugMode(self):
        self.debugMode = not self.debugMode
        # app = QtWidgets.QApplication.instance()
        # print app.styleSheet()
        if self.debugMode:
            self.m_overlay.show()
            # app.setStyleSheet("#MayaWindow {border: 5px solid red}")
        else:
            self.m_overlay.hide()
            # app.setStyleSheet("")

    # def eventFilter(self,reciever,event):
    #     # print event.type(),reciever
    #     if event.type() == QtCore.QEvent.Type.Paint:
    #         print "=========="
    #         print reciever
    #         print reciever.objectName()
    #         painter = QtGui.QPainter(reciever)
    #         fillColor = QtGui.QColor(255, 165, 0, 180)
    #         lineColor = QtGui.QColor(0, 0, 0, 255)
    #         painter.setRenderHint(QtGui.QPainter.Antialiasing)
    #         painter.setPen(QtGui.QPen(QtGui.QBrush(lineColor), 2))
    #         painter.setBrush(QtGui.QBrush(fillColor))
    #         painter.drawRoundedRect(reciever.rect(), 15, 15)
    #         painter.end()
    #         return True
    #     return False   


    # def paintEvent(self, event):
    #     window = mayaWindow()
    #     painter = QtGui.QPainter(self)
    #     fillColor = QtGui.QColor(255, 165, 0, 180)
    #     lineColor = QtGui.QColor(0, 0, 0, 255)
    #     painter.setRenderHint(QtGui.QPainter.Antialiasing)
    #     painter.setPen(QtGui.QPen(QtGui.QBrush(lineColor), 2))
    #     painter.setBrush(QtGui.QBrush(fillColor))
    #     painter.drawRoundedRect(self.rect(), 15, 15)
    #     painter.end()

    # def paintEvent(self, event):
    #     if self.debugMode:
    #         print "paint"
    #         window = mayaWindow()
    #         painter = QtGui.QPainter(window)
    #         painter.setPen(QtGui.QColor("red"))
    #         painter.drawRect(window.rect())
    #         painter.end()
        
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
        
    def getProcess(self):
        curr = time.time()

        while True:
            
            if abs(curr - time.time()) < 3:
                break

            QtCore.QCoreApplication.processEvents()
            maya.utils.processIdleEvents()
    
    def mayaShow(self,name=u"MPDB_DEBUGGER_UI"):
        
        if not cmds.workspaceControl(name,ex=1):

            toolBar = createUIComponentToolBar(name)
            toolBar.layout().addWidget(self)

            # NOTE tab widget to the command Line
            cmds.workspaceControl(name,e=1,
                dockToControl=["CommandLine","right"],
                heightProperty="fixed",
                resizeHeight= 20,
                loadImmediately= 1
            )
            toolBar.setMaximumWidth(self.maximumWidth())
            toolBar.setMaximumHeight(self.maximumHeight())

            return toolBar
        else:
            if not cmds.workspaceControl(name,q=1,vis=1):
                cmds.workspaceControl(name,e=1,vis=1)
            if cmds.workspaceControl(name,q=1,fl=1):
                cmds.evalDeferred(dedent("""
                    cmds.workspaceControl('%s',e=1,
                        dockToControl=["CommandLine","right"],
                        heightProperty="fixed",
                        resizeHeight= 20,
                        resizeWidth= 200,
                        loadImmediately= 1
                    )
                """ % name))

# import sys
# MODULE = r"F:\repo\mpdb\scripts"
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
# # debugger.m_overlay.setParent(None)