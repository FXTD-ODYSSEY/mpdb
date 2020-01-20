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
from .utils import mayaMenu
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
        # self.setEnabled(False)

        self.setAutoFillBackground(True)
        # self.setWindowFlags(QtCore.Qt.FramelessWindowHint)

    def paintEvent(self, event):
        
        # # NOTE https://stackoverflow.com/questions/51687692/how-to-paint-roundedrect-border-outline-the-same-width-all-around-in-pyqt-pysi
        # painter = QtGui.QPainter(self)
        # painter.setRenderHint(QtGui.QPainter.Antialiasing)   

        # rectPath = QtGui.QPainterPath()                      
        # height = self.height() - 4                     
        # rect = QtCore.QRectF(2, 2, self.width()-4, height)
        # rectPath.addRoundedRect(rect, 15, 15)
        # painter.setPen(QtGui.QPen(self.BorderColor, 2, QtCore.Qt.SolidLine,QtCore.Qt.RoundCap, QtCore.Qt.RoundJoin))
        # painter.drawPath(rectPath)
        # painter.setBrush(self.BackgroundColor)
        # painter.drawRoundedRect(rect, 15, 15)

        painter = QtGui.QPainter(self)
        fillColor = QtGui.QColor(255, 0, 0, 180)
        lineColor = QtGui.QColor(255, 0, 0, 255)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        painter.setPen(QtGui.QPen(QtGui.QBrush(lineColor), 2))
        painter.setBrush(QtGui.QBrush(fillColor))
        painter.drawRoundedRect(self.rect(), 0, 0)
        painter.end()

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

        cmdWndIcon = self.setUpScriptIcon()
        # print cmdWndIcon
        # cmds.symbolButton( cmdWndIcon,q=1, image=1)

        # # ptr = OpenMayaUI.MQtUtil.findControl( cmdWndIcon )
        # # self.cmdWndIcon = wrapInstance( long( ptr ), QtWidgets.QPushButton )
        # main_win = mayaWindow()
        # self.cmdWndIcon = traverseWidget4ObjectName(main_win,objectName=cmdWndIcon)
        # print dir(self.cmdWndIcon)
        # print [self.cmdWndIcon.styleSheet()]
        # print self.cmdWndIcon.windowIcon()

        # color  = QtGui.QColor("red")
        # size   = 25
        # icon   = self.debug_setting.icon()
        # pixmap = icon.pixmap(size)
        # image  = pixmap.toImage()
        # pcolor = image.pixelColor(size,size)
        # for x in range(image.width()):
        #     for y in range(image.height()):
        #         pcolor = image.pixelColor(x, y)
        #         if pcolor.alpha() > 0:
        #             color.setAlpha(pcolor.alpha())
        #             image.setPixelColor(x, y, color)
        # self.cmdWndIcon.setWindowIcon(QtGui.QIcon(QtGui.QPixmap.fromImage(image)))
        # self.cmdWndIcon.setStyleSheet("background:red;color:red")

        self.m_overlay = None
        self.debugMode = False
        # # traverseChildren(main_win)

        # layout = main_win.layout()
        # print layout
        # print layout.count()
        # for i in range(layout.count()):
        #     print i

        workspace = mel.eval("$temp = $gWorkAreaForm")
        # workspace = mayaToQT(workspace)

        # # print workspace.children()

        # flag = 0
        # for widget in main_win.children():
        #     if type(widget) == QtWidgets.QWidget:
        #         flag += 1
        #         if flag == 3:
        #             break

        # # print widget,widget.children(),widget.objectName()
        # # for _widget in widget.children():
        # #     if type(_widget) == QtWidgets.QWidget:
        # #         break

        # # print widget,flag,widget.objectName()
        # # self.m_overlay = OverLay(widget)
        # # widget.installEventFilter(self)
        
        # widget = mayaToQT(workspace)
        menu = mayaMenu()
        self.m_overlay = OverLay(menu)
        menu.installEventFilter(self)


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
        # if self.debugMode:
        #     print "red"
        #     self.setButtonColor(self.cmdWndIcon)
        # else:
        #     self.setButtonColor(self.cmdWndIcon,QtGui.QColor(215, 215, 215,0))


        # app = QtWidgets.QApplication.instance()
        # app.setStyleSheet("#MayaWindow {border: 5px solid red}" if self.debugMode else "")
        self.m_overlay.show() if self.debugMode else self.m_overlay.hide()

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
            # toolBar.setFixedHeight(0)
            # toolBar.setMaximumWidth(self.maximumWidth())
            # toolBar.setMaximumHeight(self.maximumHeight())
            toolBar.layout().addWidget(self)

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
# # debugger.m_overlay.setParent(None)