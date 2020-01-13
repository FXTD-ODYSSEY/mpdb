# coding:utf-8

__author__ =  'timmyliang'
__email__ =  '820472580@qq.com'
__date__ = '2020-01-05 21:57:02'

"""

"""

import sys
from functools import partial

from maya import cmds 
from maya import mel 
from maya import OpenMayaUI

from PySide2 import QtGui
from PySide2 import QtCore
from PySide2 import QtWidgets
from Qt.QtCompat import getCppPointer
from Qt.QtCompat import wrapInstance

# ----------------------------------------------------------------------------


def mayaToQT(name):
    """
    Maya -> QWidget

    :param str name: Maya name of an ui object
    :return: QWidget of parsed Maya name
    :rtype: QWidget
    """
    ptr = OpenMayaUI.MQtUtil.findControl( name )
    if ptr is None:         
        ptr = OpenMayaUI.MQtUtil.findLayout( name )    
    if ptr is None:         
        ptr = OpenMayaUI.MQtUtil.findMenuItem( name )
    if ptr is not None:     
        return wrapInstance( long( ptr ), QtWidgets.QWidget )


def qtToMaya(widget):
    """
    QWidget -> Maya name

    :param QWidget widget: QWidget of a maya ui object
    :return: Maya name of parsed QWidget
    :rtype: str
    """
    return OpenMayaUI.MQtUtil.fullName(
        long(
            getCppPointer(widget)[0]
        ) 
    )


# ----------------------------------------------------------------------------


def getStatusLine():
    """
    Get the QWidget of Maya's status line. 
    
    :return: QWidget of Maya's status line
    :rtype: QWidget
    """
    gStatusLine = mel.eval("$tmpVar=$gStatusLine")
    return mayaToQT(gStatusLine)

def mayaWindow():
    """
    Get Maya's main window.
    
    :rtype: QMainWindow
    """
    window = OpenMayaUI.MQtUtil.mainWindow()
    window = wrapInstance(long(window), QtWidgets.QMainWindow)
    
    return window

# ----------------------------------------------------------------------------

def createUIComponentToolBar(ControlName="CustomToolBar"):
    """createUIComponentToolBar 
    create a Maya Component Tool Bar Widget
    
    :param ControlName: str, defaults to "CustomToolBar"
    :type ControlName: str, optional
    """        

    help_line = mayaToQT("HelpLine")
    help_line.setObjectName("_HelpLine")

    mel.eval("""
    createUIComponentToolBar(
            "HelpLine", localizedUIComponentLabel("%s"), "", $gWorkAreaForm, "top", false);
    """ % ControlName)

    UIComponentToolBar = mayaToQT("HelpLine")
    UIComponentToolBar.setObjectName(ControlName)
    help_line.setObjectName("HelpLine")
    
    layout = UIComponentToolBar.layout()
    # NOTE add spacing
    layout.setContentsMargins(10,0,0,0)

    return UIComponentToolBar

# ----------------------------------------------------------------------------

def mayaShow(widget,name):
    # NOTE 如果变量存在 就检查窗口多开
    if cmds.window(name,q=1,ex=1):
        cmds.deleteUI(name)
    window = cmds.window(name,title=widget.windowTitle())
    cmds.showWindow(window)
    # NOTE 将Maya窗口转换成 Qt 组件
    ptr = mayaToQT(window)
    ptr.setLayout(QtWidgets.QVBoxLayout())
    ptr.layout().setContentsMargins(0,0,0,0)
    ptr.layout().addWidget(widget)

    return ptr

# ----------------------------------------------------------------------------

class CollapsibleWidget( QtWidgets.QWidget ):
    def __init__(self):
        super( CollapsibleWidget, self ).__init__()
        
    @staticmethod
    def install(btn,container,duration=300,expand_callback=None,collapse_callback=None):
        anim = QtCore.QPropertyAnimation(container, "maximumHeight")
        
        anim.setDuration(duration)
        anim.setStartValue(0)
        anim.setEndValue(container.sizeHint().height())
        anim.finished.connect(lambda:container.setMaximumHeight(16777215) if not btn.toggle else None)

        btn.toggle = False
        btn.setText(u"▼ %s"%btn.text())
        print container.maximumHeight()
        def toggleFn(btn,anim):
            if btn.toggle:
                btn.toggle = False
                anim.setDirection(QtCore.QAbstractAnimation.Forward)

                anim.setEndValue(CollapsibleWidget.getHeightEndValue(container))
                anim.start()
                btn.setText(u"▼%s"%btn.text()[1:])
                btn.setStyleSheet('font:normal')
                if expand_callback:
                    expand_callback()
            else:
                btn.toggle = True
                anim.setDirection(QtCore.QAbstractAnimation.Backward)
                anim.setEndValue(container.sizeHint().height())
                anim.start()
                btn.setText(u"■%s"%btn.text()[1:])
                btn.setStyleSheet('font:bold')
                if collapse_callback:
                    collapse_callback()

        func = partial(toggleFn,btn,anim)
        btn.clicked.connect(func)
        return func

    @staticmethod
    def getHeightEndValue(widget):

        parent = widget.parent()
        total_height = parent.height()

        height = 0
        for child in parent.children():
            if child == widget or not hasattr(child,"height"):
                continue
            
            height += child.height()

        prefer = widget.sizeHint().height()
        height = total_height - height
        return height if height > prefer else prefer



# ----------------------------------------------------------------------------

def install():
    from widget import Debugger_UI
    
    global MPDB_UI

    # validate channel box plus
    if MPDB_UI:
        raise RuntimeError("Channel box plus is already installed!")

    # convert status line
    statusLine = getStatusLine()
    
    # get parent
    parent = mayaWindow()
    
    # get layout        
    layout = statusLine.layout()  

    # create command search
    MPDB_UI = Debugger_UI(parent)
    layout.addWidget(MPDB_UI)
