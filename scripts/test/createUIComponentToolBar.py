
from PySide2 import QtGui
from PySide2 import QtCore
from PySide2 import QtWidgets
from Qt.QtCompat import wrapInstance

from maya import cmds 
from maya import mel 
from maya import OpenMayaUI
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

def mayaWindow():
    """
    Get Maya's main window.
    
    :rtype: QMainWindow
    """
    window = OpenMayaUI.MQtUtil.mainWindow()
    window = wrapInstance(long(window), QtWidgets.QMainWindow)
    
    return window

class TestWidget(QtWidgets.QWidget):
    def __init__(self):
        super(TestWidget,self).__init__()

        layout = QtWidgets.QVBoxLayout()
        self.setLayout(layout)

        label = QtWidgets.QLabel(u"TestWidget")
        layout.addWidget(label)

        self.show()


def traverseChildren(parent,indent="",log=True):
    if log:
        print (indent + str(parent))
        
    if not hasattr(parent,"children"):
        return

    for child in parent.children():
        traverseChildren(child,indent=indent+"    ")

def createUIComponentToolBar(ControlName="MyToolBar"):
    if cmds.workspaceControl(ControlName,ex=1):
        cmds.deleteUI(ControlName)
        

    help_line = mayaToQT("HelpLine")
    help_line.setObjectName("_HelpLine")

    mel.eval("""
    createUIComponentToolBar(
            "HelpLine", localizedUIComponentLabel("HelpLine"), "", $gWorkAreaForm, "top", false);
    """)

    UIComponentToolBar = mayaToQT("HelpLine")
    UIComponentToolBar.setObjectName(ControlName)
    help_line.setObjectName("HelpLine")
    
    layout = toolBar.layout()
    layout.setContentsMargins(10,0,0,0)
    toolBar.setFixedHeight(20)

    return UIComponentToolBar

if __name__ == "__main__":
    
    toolBar = createUIComponentToolBar("MyToolBar")
    
    cmds.workspaceControl("MyToolBar",e=1,dockToControl=["StatusLine","right"])
    # cmds.deleteUI("MyToolBar")