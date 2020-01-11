# coding:utf-8

import os
import sys


from PySide2 import QtGui
from PySide2 import QtCore
from PySide2 import QtWidgets
from Qt.QtCompat import loadUi
from Qt.QtCompat import wrapInstance

from maya import cmds
from maya import mel
from maya import OpenMayaUI

from textwrap import dedent

class Debugger_UI(QtWidgets.QWidget):
    def __init__(self):
        super(Debugger_UI,self).__init__()
        self.checkNum = 0
        self.check = True
        layout = QtWidgets.QVBoxLayout()
        self.setLayout(layout)
        
        win = cmds.window()
        cmds.columnLayout()
        executor = cmds.cmdScrollFieldExecuter(
            showTooltipHelp=0,
            objectPathCompletion=0,
            autoCloseBraces=0,
            commandCompletion=0,
            searchWraps=0,
            showLineNumbers=1,
            sourceType="python")
        executor_ptr = self.mayaToQT(executor)
        layout.addWidget(executor_ptr)
        cmds.deleteUI(win)

        document =  self.traverseWidget(executor_ptr, QtGui.QTextDocument)

        document.setPlainText(dedent(u"""
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

                    ui_path = os.path.join(DIR,"icon","debug.ui")
                    loadUi(ui_path,self)
                    # layout = self.QHBoxLayout()
                    # self.setLayout(layout)

                def getProcess(self):
                    curr = time.time()

                    while True:
                        
                        if abs(curr - time.time()) < 3:
                            break

                        QtCore.QCoreApplication.processEvents()
                        maya.utils.processIdleEvents()
                
                def mayaShow(self,name=u"MPDB_DEBUGGER_UI"):
                    # NOTE 如果变量存在 就检查窗口多开
                    if cmds.window(name,q=1,ex=1):
                        cmds.deleteUI(name)
                    window = cmds.window(name,title=self.windowTitle())
                    cmds.showWindow(window)
                    # NOTE 将Maya窗口转换成 Qt 组件
                    ptr = self.mayaToQT(window)
                    ptr.setLayout(QtWidgets.QVBoxLayout())
                    ptr.layout().setContentsMargins(0,0,0,0)
                    ptr.layout().addWidget(self)
                    ptr.destroyed.connect(self._close)

                    ptr.setWindowTitle(self.windowTitle())
                    ptr.setMaximumHeight(self.maximumHeight())
                    ptr.setMaximumWidth(self.maximumWidth())
                    
                def _close(self):
                    # NOTE 脱离要删除的窗口
                    window = OpenMayaUI.MQtUtil.mainWindow()
                    window = wrapInstance(long(window), QtWidgets.QMainWindow)
                    self.setParent(window)
                
                def mayaToQT( self,name ):
                    # Maya -> QWidget
                    ptr = OpenMayaUI.MQtUtil.findControl( name )
                    if ptr is None:     ptr = OpenMayaUI.MQtUtil.findLayout( name )
                    if ptr is None:     ptr = OpenMayaUI.MQtUtil.findMenuItem( name )
                    if ptr is not None: return wrapInstance( long( ptr ), QtWidgets.QWidget )

            # import sys
            # MODULE = r""F:\repo\mpdb\scripts\mpdb""
            # if MODULE not in sys.path:
            #     sys.path.append(MODULE)
            # import widget
            # reload(widget)

            # debugger = widget.Debugger_UI()
            # debugger.show()

            """))

        cmds.cmdScrollFieldExecuter(executor,e=1,currentLine=13)
        # print "lineCount",document.lineCount()
        # print "blockCount",document.blockCount()

        # edit =  self.traverseWidget(executor_ptr, QtWidgets.QTextEdit)
        # self.traverseScroll(executor_ptr)

        # cursor = QtGui.QTextCursor(document)
        # cursor.movePosition(QtGui.QTextCursor.Start,n=3)
        # edit.setTextCursor(cursor)
        # edit.verticalScrollBar().setValue(0)


        # text =  self.traverseScroll(executor_ptr)
        # text =  self.traverseWidget(executor_ptr,QtGui.QAbstractTextDocumentLayout)
        # text.format(3)
        # print scroll
        # print dir(scroll)
        # scroll.setValue(25)

    def traverseWidget(self,parent,widget_type=None):
        if not hasattr(parent,"children"):
            return
        if type(parent) == widget_type:
            return parent

        for child in parent.children():
            parent = self.traverseWidget(child,widget_type)
            if parent:
                return parent

    def traverseScroll(self,parent):
        if not hasattr(parent,"children"):
            return
        if type(parent) == QtWidgets.QTextEdit:
            print "scroll",parent.verticalScrollBar().value()
            # return parent

        for child in parent.children():
            self.traverseScroll(child)

    def mayaShow(self,name=u"MPDB_DEBUGGER_UI"):
        # NOTE 如果变量存在 就检查窗口多开
        if cmds.window(name,q=1,ex=1):
            cmds.deleteUI(name)
        window = cmds.window(name,title=self.windowTitle())
        cmds.showWindow(window)
        # NOTE 将Maya窗口转换成 Qt 组件
        ptr = self.mayaToQT(window)
        ptr.setLayout(QtWidgets.QVBoxLayout())
        ptr.layout().setContentsMargins(0,0,0,0)
        ptr.layout().addWidget(self)

        ptr.setWindowTitle(self.windowTitle())
        ptr.setMaximumHeight(self.maximumHeight())
        ptr.setMaximumWidth(self.maximumWidth())

    def mayaToQT( self,name ):
        # Maya -> QWidget
        ptr = OpenMayaUI.MQtUtil.findControl( name )
        if ptr is None:     ptr = OpenMayaUI.MQtUtil.findLayout( name )
        if ptr is None:     ptr = OpenMayaUI.MQtUtil.findMenuItem( name )
        if ptr is not None: return wrapInstance( long( ptr ), QtWidgets.QWidget )

if __name__ == "__main__":
    debugger = Debugger_UI()
    debugger.mayaShow()