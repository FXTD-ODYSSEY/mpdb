from Qt import QtCore
from Qt import QtWidgets
from Qt import QtGui
from Qt.QtCompat import wrapInstance

from maya import cmds
from maya import OpenMayaUI

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



class MiddleClickSignal(QtCore.QObject):
    """addExecuteShortcut 监听鼠标中键事件
    """
    middleClicked = QtCore.Signal()
    def __init__(self,parent):
        super(MiddleClickSignal,self).__init__()
        # NOTE 确保自己不会被垃圾回收掉
        self.setParent(parent)
        parent.installEventFilter(self)
        
    def eventFilter(self,reciever,event):
        if event.type() == QtCore.QEvent.Type.MouseButtonPress:
            if event.button() == QtCore.Qt.MidButton:
                self.middleClicked.emit()
                return True
        return False

class TestWidget(QtWidgets.QWidget):
    
    def __init__(self):
        super(TestWidget, self).__init__()

        self.button = QtWidgets.QPushButton(u"middle click")

        layout  = QtWidgets.QVBoxLayout()

        self.setLayout(layout)
        layout.addWidget(self.button)

        Setting_signal = MiddleClickSignal(self.button)
        Setting_signal.middleClicked.connect(self.middleClickEvent)

    def middleClickEvent(self):
        print "middle click"

    def mayaShow(self,name="TestWidget"):

        # NOTE 如果变量存在 就检查窗口多开
        if cmds.window(name,q=1,ex=1):
            cmds.deleteUI(name)
        window = cmds.window(name,title=self.windowTitle())
        cmds.showWindow(window)
        # NOTE 将Maya窗口转换成 Qt 组件
        ptr = mayaToQT(window)
        ptr.setLayout(QtWidgets.QVBoxLayout())
        ptr.layout().setContentsMargins(0,0,0,0)
        ptr.layout().addWidget(self)

        return ptr


if __name__ == "__main__":
    widget = TestWidget()
    window = widget.mayaShow()