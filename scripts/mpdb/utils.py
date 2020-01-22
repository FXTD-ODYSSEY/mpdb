# coding:utf-8

__author__ =  'timmyliang'
__email__ =  '820472580@qq.com'
__date__ = '2020-01-05 21:57:02'

"""
utility function
"""

import sys
from functools import partial

from maya import cmds 
from maya import mel 
from maya import OpenMayaUI

from Qt import QtGui
from Qt import QtCore
from Qt import QtWidgets
from Qt.QtCompat import getCppPointer
from Qt.QtCompat import wrapInstance

# ----------------------------------------------------------------------------


def mayaToQT(name,wrapType=QtWidgets.QWidget):
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
        return wrapInstance( long( ptr ), wrapType )


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


def mayaMenu():
    """
    Find Maya's main menu bar.
    
    :rtype: QMenuBar
    """
    for m in mayaWindow().children():
        if type(m) == QtWidgets.QMenuBar:
            return m
# ----------------------------------------------------------------------------

def createUIComponentToolBar(ControlName="CustomToolBar"):
    """createUIComponentToolBar 
    create a Maya Component Tool Bar Widget
    
    :param ControlName: str, defaults to "CustomToolBar"
    :type ControlName: str, optional
    """        

    help_line = mayaToQT("HelpLine")
    help_line.setObjectName("_HelpLine")

    cmds.workspaceControl("HelpLine",
        label=ControlName,
        loadImmediately= 1,
        initialHeight=20,
        heightProperty="fixed",
    )
   
    # mel.eval("""
    # createUIComponentToolBar("HelpLine", localizedUIComponentLabel("%s"), "", $gWorkAreaForm, "top", false);
	# workspaceControl -e -initialHeight 20 -heightProperty "fixed" $helpLineWorkspaceControl;
    # """ % ControlName)

    UIComponentToolBar = mayaToQT("HelpLine")
    UIComponentToolBar.setObjectName(ControlName)
    help_line.setObjectName("HelpLine")
    
    layout = UIComponentToolBar.layout()
    # NOTE add spacing
    layout.setContentsMargins(10,0,0,0)

    return UIComponentToolBar

# ----------------------------------------------------------------------------

def mayaShow(widget,name):
    """mayaShow 
    show the widget in the Maya native window
    
    :param widget: widget to add 
    :type widget: QWidget
    :param name: maya window name
    :type name: str
    :return: maya window pointer
    :rtype: QWidget
    """
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

def traverseChildren(parent,indent="",log=True):
    """traverseChildren 
    Traverse into the widget children | print the children hierarchy
    
    :param parent: traverse widget
    :type parent: QWidget
    :param indent: indentation space, defaults to ""
    :type indent: str, optional
    :param log: print the data, defaults to True
    :type log: bool, optional
    """        
    if log:
        print ("%s%s %s" % (indent,parent,parent.objectName()))
        
    if not hasattr(parent,"children"):
        return

    for child in parent.children():
        traverseChildren(child,indent=indent+"    ")

        
def traverseWidget4ObjectName(parent,objectName=None):
    """traverseChildren 
    Traverse into the widget children | print the children hierarchy
    
    :param parent: traverse widget
    :type parent: QWidget
    :param indent: indentation space, defaults to ""
    :type indent: str, optional
    :param log: print the data, defaults to True
    :type log: bool, optional
    """        

    
    if not hasattr(parent,"children") or not hasattr(parent,"objectName"):
        return
    
    if parent.objectName() == objectName:
        return parent

    for child in parent.children():
        widget = traverseWidget4ObjectName(child,objectName)
        if widget:
            return widget

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

        widget.updateGeometry()
        prefer = widget.sizeHint().height()
        height = total_height - height
        return height if height > prefer else prefer


# ----------------------------------------------------------------------------

def replaceWidget(src,dst):
    u"""replaceWidget 替换组件
    
    Parameters
    ----------
    src : QWidget
        源组件
    dst : QWidget
        目标组件
    
    Returns
    -------
    QWidget
        [description]
    """
    updateWidgetState(src,dst)
    layout = src.parent().layout()
    layout,index = getTargetLayoutIndex(layout,src)
    if not layout:
        print u"没有找到 %s 的 Layout，替换失败" % src
        return src

    layout.insertWidget(index,dst)
    src.setParent(None)
    
    return dst

def updateWidgetState(src,dst):
    u"""updateWidgetState 同步组件状态
    
    Parameters
    ----------
    src : QWidget
        源组件
    dst : QWidget
        目标组件
    """
    dst.setAcceptDrops            (src.acceptDrops())
    dst.setAccessibleDescription  (src.accessibleDescription())
    dst.setBackgroundRole         (src.backgroundRole())
    dst.setBaseSize               (src.baseSize())
    dst.setContentsMargins        (src.contentsMargins())
    dst.setContextMenuPolicy      (src.contextMenuPolicy())
    dst.setCursor                 (src.cursor())
    dst.setFocusPolicy            (src.focusPolicy())
    dst.setFocusProxy             (src.focusProxy())
    dst.setFont                   (src.font())
    dst.setForegroundRole         (src.foregroundRole())
    dst.setGeometry               (src.geometry())
    dst.setInputMethodHints       (src.inputMethodHints())
    dst.setLayout                 (src.layout())
    dst.setLayoutDirection        (src.layoutDirection())
    dst.setLocale                 (src.locale())
    dst.setMask                   (src.mask())
    dst.setMaximumSize            (src.maximumSize())
    dst.setMinimumSize            (src.minimumSize())
    dst.setMouseTracking          (src.hasMouseTracking ())
    dst.setPalette                (src.palette())
    dst.setParent                 (src.parent())
    dst.setSizeIncrement          (src.sizeIncrement())
    dst.setSizePolicy             (src.sizePolicy())
    dst.setStatusTip              (src.statusTip())
    dst.setStyle                  (src.style())
    dst.setToolTip                (src.toolTip())
    dst.setUpdatesEnabled         (src.updatesEnabled())
    dst.setWhatsThis              (src.whatsThis())
    dst.setWindowFilePath         (src.windowFilePath())
    dst.setWindowFlags            (src.windowFlags())
    dst.setWindowIcon             (src.windowIcon())
    dst.setWindowIconText         (src.windowIconText())
    dst.setWindowModality         (src.windowModality())
    dst.setWindowOpacity          (src.windowOpacity())
    dst.setWindowRole             (src.windowRole())
    dst.setWindowState            (src.windowState())


def getTargetLayoutIndex(layout,target):
    u"""getTargetLayoutIndex 获取目标 Layout 和 序号
    
    Parameters
    ----------
    layout : QLayout 
        通过 QLayout 递归遍历下属的组件
    target : QWidget
        要查询的组件
    
    Returns
    -------
    layout : QLayout
        查询组件所在的 Layout
    i : int
        查询组件所在的 Layout 的序号
    """
    count = layout.count()
    for i in range(count):
        item = layout.itemAt(i).widget()
        if item == target:
            return layout,i
    else:
        for child in layout.children():
            layout,i = getTargetLayoutIndex(child,target)
            if layout:
                return layout,i
        return [None,None]

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
