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
from .utils import mayaToQT

from PySide2 import QtGui
from PySide2 import QtCore
from PySide2 import QtWidgets
from Qt.QtCompat import loadUi
from Qt.QtCompat import wrapInstance

from maya import cmds
from maya import mel
from maya import OpenMayaUI


DIR = os.path.dirname(__file__)

class Debugger_UI(QtWidgets.QWidget):
    def __init__(self):
        super(Debugger_UI,self).__init__()

        ui_path = os.path.join(DIR,"ui","debug.ui")
        loadUi(ui_path,self)

        self.debugMode = False

        self.setButtonColor(self.debug_continue,QtGui.QColor(117, 190, 255))
        self.setButtonColor(self.debug_step_over,QtGui.QColor(117, 190, 255))
        self.setButtonColor(self.debug_step_into,QtGui.QColor(117, 190, 255))
        self.setButtonColor(self.debug_step_out,QtGui.QColor(117, 190, 255))
        self.setButtonColor(self.debug_cancel)
        self.setButtonColor(self.debug_setting,QtGui.QColor(215, 215, 215))

        self.debug_icon.setEnabled(False)
        self.debug_setting.clicked.connect(self.startDebugMode)

        self.setUpScriptMenu()
        
    def setUpScriptMenu(self):
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
        pass
        
    def startDebugMode(self):
        self.debugMode = not self.debugMode
        app = QtWidgets.QApplication.instance()
        # print app.styleSheet()
        if self.debugMode:
            app.setStyleSheet("#MayaWindow {border: 5px solid red}")
        else:
            app.setStyleSheet("")

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