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
from functools import wraps
from functools import partial

import toolbar_rc

from .utils import createUIComponentToolBar
from .utils import mayaWindow
from .utils import getStatusLine
from .utils import traverseChildren
from .utils import mayaToQT

from .scriptEditor import enhanceScriptEditor

from .panel import Debugger_Panel

from PySide2 import QtGui
from PySide2 import QtCore
from PySide2 import QtWidgets
from Qt.QtCompat import loadUi
from Qt.QtCompat import wrapInstance
from Qt.QtCompat import translate


import maya
from maya import cmds
from maya import mel
from maya import OpenMayaUI


DIR = os.path.dirname(__file__)

# class OverLay(QtWidgets.QWidget):
#     """OverLay 红框Debug标记 暂时弃用"""
#     BorderColor     = QtGui.QColor(255, 0, 0, 255)     
#     BackgroundColor = QtGui.QColor(255, 255, 255, 0) 
    
#     def __init__(self, *args, **kwargs):
#         QtWidgets.QWidget.__init__(self, *args, **kwargs)
#         self.setAttribute(QtCore.Qt.WA_NoSystemBackground)
#         self.setAttribute(QtCore.Qt.WA_TransparentForMouseEvents)
#         self.setWindowFlags(QtCore.Qt.WindowTransparentForInput|QtCore.Qt.FramelessWindowHint)
#         self.setFocusPolicy( QtCore.Qt.NoFocus )
#         self.hide()
#         # self.setEnabled(False)

#         self.setAutoFillBackground(True)
#         # self.setWindowFlags(QtCore.Qt.FramelessWindowHint)

#     def paintEvent(self, event):
        
#         # NOTE https://stackoverflow.com/questions/51687692/how-to-paint-roundedrect-border-outline-the-same-width-all-around-in-pyqt-pysi
#         painter = QtGui.QPainter(self)
#         painter.setRenderHint(QtGui.QPainter.Antialiasing)   

#         rectPath = QtGui.QPainterPath()                      
#         height = self.height() - 4                     
#         rect = QtCore.QRectF(2, 2, self.width()-4, height)
#         rectPath.addRoundedRect(rect, 15, 15)
#         painter.setPen(QtGui.QPen(self.BorderColor, 2, QtCore.Qt.SolidLine,QtCore.Qt.RoundCap, QtCore.Qt.RoundJoin))
#         painter.drawPath(rectPath)
#         painter.setBrush(self.BackgroundColor)
#         painter.drawRoundedRect(rect, 15, 15)

def setDebugMode(func):
    """setDebugMode Debug 装饰器
    """
    @wraps(func)
    def wrapper(self,*args, **kwargs):
        main_win = mayaWindow()
        # NOTE Maya 红框标记
        main_win.setStyleSheet("#MayaWindow {background:red}")
        # NOTE 激活 Debug 按钮
        self.debug_icon.setEnabled(True)
        args = func(self,*args, **kwargs)
        self.debug_icon.setEnabled(False)
        main_win.setStyleSheet("")
        print "return args: '%s'" % args
        return args
    return wrapper

class Divider(QtWidgets.QWidget):     
    """
    Divider widget that is used in the manager menu and the commands overview.
    """
    def __init__(self,text = None):
        super(Divider,self).__init__()
        
        # style sheets
        labelSS = "QLabel{font: bold; color: orange; border: 0px;}"
        frameSS = "QFrame{color: gray; margin: 0 12 0 12;}"
        
        # create widgets
        self.label = QtWidgets.QLabel(self)
        self.label.setFixedHeight(12)
        self.label.setStyleSheet(labelSS)
        
        sep01 = QtWidgets.QFrame(self)
        sep02 = QtWidgets.QFrame(self)
        
        for sep in [sep01,sep02]:
            sep.setStyleSheet(frameSS)
            sep.setFrameStyle(QtWidgets.QFrame.HLine)
            sep.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        
        # create layout
        layout = QtWidgets.QHBoxLayout(self)
        layout.addWidget(sep01)
        layout.addWidget(self.label)
        layout.addWidget(sep02)
                
        layout.setContentsMargins(0,0,0,0)
        layout.setSpacing(0)
        self.setFixedHeight(12)

        if text:
            self.setText(text)

    def setText(self,text):
        self.label.setText(text)

class MiddleClickSignal(QtCore.QObject):
    """addExecuteShortcut 监听鼠标中键事件
    """
    middleClicked = QtCore.Signal()
    def __init__(self,parent):
        super(MiddleClickSignal,self).__init__()
        self.setParent(parent)
        parent.installEventFilter(self)
        
    def eventFilter(self,reciever,event):
        if event.type() == QtCore.QEvent.Type.MouseButtonPress:
            if event.button() == QtCore.Qt.MidButton:
                self.middleClicked.emit()
                return True
        return False

class Debugger_UI(QtWidgets.QWidget):

    windowName = "MPDB_Debugger_UI"

    def __init__(self):
        super(Debugger_UI,self).__init__()

        self.__lang_list = {}
        self.debug_continue_state   = False
        self.debug_step_over_state  = False
        self.debug_step_into_state  = False
        self.debug_step_out_state   = False
        self.debug_cancel_state     = False
        self.debug_cancel_run_state = False
        self.debug_pdb_state        = False
        

        # NOTE 添加 Ctrl + E 执行快捷键 | 修复 Maya 2017 崩溃问题
        enhanceScriptEditor()

        # NOTE 加载 UI 文件
        ui_path = os.path.join(DIR,"ui","debug.ui")
        loadUi(ui_path,self)
        
        # NOTE 设置 Debug 图标颜色
        self.setButtonColor(self.debug_continue,QtGui.QColor(117, 190, 255))
        self.setButtonColor(self.debug_step_over,QtGui.QColor(117, 190, 255))
        self.setButtonColor(self.debug_step_into,QtGui.QColor(117, 190, 255))
        self.setButtonColor(self.debug_step_out,QtGui.QColor(117, 190, 255))
        self.setButtonColor(self.debug_cancel)
        self.setButtonColor(self.debug_setting,QtGui.QColor(215, 215, 215))

        # NOTE 默认禁用 Debug 图标
        self.debug_icon.setEnabled(False)
        # NOTE 生成 Debug 面板
        self.panel = Debugger_Panel(self)

        # NOTE 设置 Debug 图标事件
        self.debug_continue.clicked.connect(partial(self.setContinue,True))
        self.debug_step_over.clicked.connect(partial(self.setStep_over,True))
        self.debug_step_into.clicked.connect(partial(self.setStep_into,True))
        self.debug_step_out.clicked.connect(partial(self.setStep_out,True))
        self.debug_cancel.clicked.connect(partial(self.setCancel,True))
        self.debug_setting.clicked.connect(self.openPanel)

        # NOTE 添加鼠标中键打开 Debug 图标
        self.setupScriptIconMiddleClick()
        # NOTE 添加鼠标中键 点击 setting 图标 使用 pdb 模式 Debug
        self.setupDebugSettingMiddleClick()
        # NOTE 添加鼠标中键 点击 cancel 图标 执行后续代码
        self.setupDebugCancelMiddleClick()

        # NOTE 加载翻译器
        self.trans = QtCore.QTranslator(self)

        # NOTE setting 图标添加 右键菜单
        self.debug_setting.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.debug_setting.customContextMenuRequested.connect(self.showSettingMenu)

        # NOTE 初始化 setting 右键菜单
        self.setting_menu = QtWidgets.QMenu(self)
        self.i18n_seperator = Divider()
        action = QtWidgets.QWidgetAction(self)
        action.setDefaultWidget(self.i18n_seperator)
        self.setting_menu.addAction(action)

        self.localeList = {
            "zh_CN":u"中文",
            "en_US":u"English",
        }

        self.retranslateUi()
    
    def retranslateUi(self):
        # NOTE pdb 输入框
        self.pdb_title = QtWidgets.QApplication.translate("pdb", "pdb Input Mode")
        self.pdb_msg = QtWidgets.QApplication.translate("pdb", "Input pdb Debug Command")
        # NOTE 设置图标提示
        self.debug_continue_tip = QtWidgets.QApplication.translate("icon", "Debug Continue")
        self.debug_step_over_tip = QtWidgets.QApplication.translate("icon", "Debug Step Over")
        self.debug_step_into_tip = QtWidgets.QApplication.translate("icon", "Debug Step Into")
        self.debug_step_out_tip = QtWidgets.QApplication.translate("icon", "Debug Step Out")
        self.debug_cancel_tip = QtWidgets.QApplication.translate("icon", "LMB Stop Debug | MMB Ignore Breakpoint")
        self.debug_setting_tip = QtWidgets.QApplication.translate("icon", "LMB Open Debug Panel | MMB pdb Input Mode | RMB Switch Language")

        self.debug_continue.setStatusTip(self.debug_continue_tip)
        self.debug_continue.setToolTip(self.debug_continue_tip)
        self.debug_step_over.setStatusTip(self.debug_step_over_tip)
        self.debug_step_over.setToolTip(self.debug_step_over_tip)
        self.debug_step_into.setStatusTip(self.debug_step_into_tip)
        self.debug_step_into.setToolTip(self.debug_step_into_tip)
        self.debug_step_out.setStatusTip(self.debug_step_out_tip)
        self.debug_step_out.setToolTip(self.debug_step_out_tip)
        self.debug_cancel.setStatusTip(self.debug_cancel_tip)
        self.debug_cancel.setToolTip(self.debug_cancel_tip)
        self.debug_setting.setStatusTip(self.debug_setting_tip)
        self.debug_setting.setToolTip(self.debug_setting_tip)
        
        # NOTE 右键菜单
        self.i18n_mode = QtWidgets.QApplication.translate("i18n", "Language Mode")
        self.i18n_seperator.setText(self.i18n_mode)

        # NOTE 窗口名称
        if cmds.workspaceControl(self.windowName,q=1,ex=1):
            toolbar_name = QtWidgets.QApplication.translate("window", "Maya Debugger Toolbar")
            cmds.workspaceControl(self.windowName,e=1,label=toolbar_name)
        if cmds.window(self.panel.windowName,q=1,ex=1):
            panel_name = QtWidgets.QApplication.translate("window", "Maya Debugger Panel")
            cmds.window(self.panel.windowName,e=1,title=panel_name)

    @property
    def localeList(self):
        return self.__lang_list
    
    @localeList.setter
    def localeList(self,value):
        if type(value) != dict:
            return
        self.__lang_list = value
        system_lang = QtCore.QLocale.system().name()
        i18n_folder = os.path.join(DIR,"i18n")
        for name,label in self.__lang_list.items():
            action = QtWidgets.QAction(label, self)
            qm_file = os.path.join(i18n_folder,"%s.qm" % name)
            qm_file = qm_file if os.path.exists(qm_file) else None
            action.triggered.connect(partial(self.i18nInstall,qm_file))
            self.setting_menu.addAction(action)
            # NOTE 判断系统语言进行注册
            if system_lang == name:
                self.i18nInstall(qm_file)

    def i18nInstall(self,qm_path):
        if qm_path and os.path.exists(qm_path):
            self.trans.load(qm_path)
            QtWidgets.QApplication.instance().installTranslator(self.trans)
        else:
            QtWidgets.QApplication.instance().removeTranslator(self.trans)

    def changeEvent(self, event):
        if event.type() == QtCore.QEvent.LanguageChange:
            self.retranslateUi()
        super(Debugger_UI, self).changeEvent(event)
        
    def showSettingMenu(self, point):
        self.setting_menu.exec_(self.debug_setting.mapToGlobal(point))        

    def setupScriptIconMiddleClick(self):
        # NOTE 获取 脚本编辑器 图标按钮
        gCommandLineForm = mel.eval('$tempVar = $gCommandLineForm')
        commandLineForm = cmds.formLayout(gCommandLineForm, q=1, ca=1)[0]
        cmdWndIcon = cmds.formLayout(commandLineForm, q=1, ca=1)[-1]
        cmdWnd = mayaToQT(cmdWndIcon)

        # NOTE 添加中键点击信号
        self.scriptIcon_signal = MiddleClickSignal(cmdWnd)
        self.scriptIcon_signal.middleClicked.connect(self.mayaShow)

        return cmdWndIcon
    
    def setupDebugSettingMiddleClick(self):
        self.Setting_signal = MiddleClickSignal(self.debug_setting)
        self.Setting_signal.middleClicked.connect(partial(self.setPdb,True))

    def setupDebugCancelMiddleClick(self):
        self.Cancel_signal = MiddleClickSignal(self.debug_cancel)
        self.Cancel_signal.middleClicked.connect(partial(self.setCancelRun,True))

    def openPanel(self):
        self.panel_win = self.panel.mayaShow()
        self.retranslateUi()

    def setContinue(self,state):
        self.debug_continue_state  = state

    def setStep_over(self,state):
        self.debug_step_over_state  = state

    def setStep_into(self,state):
        self.debug_step_into_state  = state

    def setStep_out(self,state):
        self.debug_step_out_state   = state

    def setCancel(self,state):
        self.debug_cancel_state     = state

    def setCancelRun(self,state):
        self.debug_cancel_run_state = state

    def setPdb(self,state):
        if self.debug_icon.isEnabled():
            self.debug_pdb_state = state

    def setButtonColor(self,button,color=QtGui.QColor("red"),size=25):
        """setButtonColor set SVG Icon Color
        
        Parameters
        ----------
        button : QPushButton
            Icon Button
        color : QColor, optional
            set the Icon color, by default QtGui.QColor("red")
        size : int, optional
            icon size, by default 25
        """
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
        
    @setDebugMode
    def breakpoint(self,MPDB,frame):
        import time 
        curr = time.time()
        while True:
            elapsed = abs(time.time() - curr)
            print elapsed
            if elapsed > 2:
                print "elpased"
                return "q"

            if self.debug_continue_state  :
                self.debug_continue_state  = False
                return "c"

            elif self.debug_step_over_state :
                self.debug_step_over_state = False
                return "n"

            elif self.debug_step_into_state :
                self.debug_step_into_state = False
                return "s"

            elif self.debug_step_out_state  :
                self.debug_step_out_state  = False
                return "u;;n"

            elif self.debug_cancel_state    :
                self.debug_cancel_state    = False
                return "disable;;q"

            elif self.debug_cancel_run_state    :
                self.debug_cancel_run_state    = False
                return "disable;;c"

            elif self.debug_pdb_state    :
                self.debug_pdb_state    = False
                text,ok = QtWidgets.QInputDialog.getText(self,self.pdb_title,self.pdb_msg)
                if ok and text:
                    return text

            # NOTE Keep Maya alive 
            QtCore.QCoreApplication.processEvents()
            maya.utils.processIdleEvents()
    
    def closeEvent(self,event):
        # NOTE 停止 Debug 模式
        if self.debug_icon.isEnabled():
            self.debug_cancel_state = True
            
        if cmds.workspaceControl(self.windowName,q=1,ex=1):
            cmds.evalDeferred("cmds.deleteUI('%s')" % self.windowName)

        panel_name = self.panel.windowName
        if cmds.window(panel_name,q=1,ex=1):
            cmds.evalDeferred("cmds.deleteUI('%s')" % panel_name)

    def mayaShow(self):
        name = self.windowName
        if not cmds.workspaceControl(name,ex=1):
            
            toolBar = createUIComponentToolBar(name)
            cmds.workspaceControl(name,e=1,r=1)
            toolBar.layout().addWidget(self)
            self.retranslateUi()
            # NOTE Tab widget to the command Line
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
        
        
