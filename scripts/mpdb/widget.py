# coding:utf-8

__author__ =  'timmyliang'
__email__ =  '820472580@qq.com'
__date__ = '2020-01-05 22:10:22'

"""
Debugger UI setup
"""
import os
import sys
import debug_rc


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

