# coding:utf-8

__author__ =  'timmyliang'
__email__ =  '820472580@qq.com'
__date__ = '2020-01-05 21:57:02'

"""

"""

from maya import OpenMayaUI
from maya import cmds 
from maya import mel 

from PySide2 import QtGui
from PySide2 import QtCore
from PySide2 import QtWidgets

from widget import Debugger_UI
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
        return shiboken.wrapInstance( long( ptr ), QtWidgets.QWidget )


def qtToMaya(widget):
    """
    QWidget -> Maya name

    :param QWidget widget: QWidget of a maya ui object
    :return: Maya name of parsed QWidget
    :rtype: str
    """
    return OpenMayaUI.MQtUtil.fullName(
        long(
            shiboken.getCppPointer(widget)[0]
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
    window = shiboken.wrapInstance(long(window), QtWidgets.QMainWindow)
    
    return window

# ----------------------------------------------------------------------------



def install():
    
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
