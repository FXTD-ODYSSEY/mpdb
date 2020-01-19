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

from .utils import CollapsibleWidget
from .utils import mayaShow
from .utils import replaceWidget

from Qt import QtGui
from Qt import QtCore
from Qt import QtWidgets
from Qt.QtCompat import loadUi
from Qt.QtCompat import wrapInstance

from maya import cmds
from maya import mel
from maya import OpenMayaUI

from codeEditor import  CodeEditor

DIR = os.path.dirname(__file__)

class LineEditDelegate(QtWidgets.QStyledItemDelegate):

    moveCurrentCellBy = QtCore.Signal(int, int)

    def __init__(self, parent=None):
        super(LineEditDelegate, self).__init__(parent)

    def createEditor(self, parent, option, index):
        self.editor = QtWidgets.QLineEdit(parent)
        self.editor.setFrame(False)
        self.editor.installEventFilter(self)
        return self.editor

    def setEditorData(self, editor, index):
        """setEditorData 
        Get cell data to lineEdit 
        
        :param editor: lineEdit widget
        :type editor: QLineEdit
        :param index: cell index
        :type index: QtCore.QModelIndex
        """
        value = index.model().data(index, QtCore.Qt.EditRole)
        editor.setText(value)

    def setModelData(self, editor, model, index):
        value = editor.text()
        model.setData(index, value, QtCore.Qt.EditRole)

    def updateEditorGeometry(self, editor, option, index):
        editor.setGeometry(option.rect)

    def eventFilter(self, target, event):
        if target is self.editor:
            # NOTE 点击其他地方 取消修改
            if event.type() == QtCore.QEvent.Type.FocusAboutToChange:
                self.closeEditor.emit(self.editor, QtWidgets.QAbstractItemDelegate.NoHint)
                
            if event.type() == QtCore.QEvent.KeyPress:

                if event.key() in (QtCore.Qt.Key_Return, QtCore.Qt.Key_Enter):
                    print "press enter"
                    self.commitData.emit(self.editor)
                    self.closeEditor.emit(self.editor, QtWidgets.QAbstractItemDelegate.NoHint)

                if self.editor.hasFocus():
                    # NOTE 阻断上下箭头的 Layout
                    if event.key() in [QtCore.Qt.Key_Down,QtCore.Qt.Key_Up]:
                        return True
                    return False

                moveCell, row, column = False, 0, 0
                if event.key() == QtCore.Qt.Key_Down:
                    moveCell, row, column = True, 1, 0
                if event.key() == QtCore.Qt.Key_Up:
                    moveCell, row, column = True, -1, 0
                if event.key() in (QtCore.Qt.Key_Right, QtCore.Qt.Key_Tab):
                    moveCell, row, column = True, 0, 1
                if event.key() in (QtCore.Qt.Key_Left, QtCore.Qt.Key_Backtab):
                    moveCell, row, column = True, 0, -1

                if moveCell:
                    self.commitData.emit(self.editor)
                    self.closeEditor.emit(self.editor, QtWidgets.QAbstractItemDelegate.NoHint)
                    self.moveCurrentCellBy.emit(row, column)
                    return True

            
        return False   

class FilterTableWidget(QtWidgets.QWidget):
    """
    # NOTE https://stackoverflow.com/questions/14068823/how-to-create-filters-for-qtableview-in-pyqt
    """
    def __init__(self, parent=None):
        super(FilterTableWidget, self).__init__(parent)
        self.lineEdit       = QtWidgets.QLineEdit(self)
        self.view           = QtWidgets.QTableView(self)
        self.comboBox       = QtWidgets.QComboBox(self)
        self.label          = QtWidgets.QLabel(self)

        # NOTE 延长Header
        self.view.horizontalHeader().setStretchLastSection(True)            

        self.view.setWordWrap(True)
        self.view.setTextElideMode(QtCore.Qt.ElideMiddle)
        self.view.resizeRowsToContents()

        delegate = LineEditDelegate()
        self.view.setItemDelegate(delegate)

        self.gridLayout = QtWidgets.QGridLayout(self)
        self.gridLayout.setContentsMargins(0,0,0,0)
        self.gridLayout.addWidget(self.lineEdit, 0, 1, 1, 1)
        self.gridLayout.addWidget(self.view, 1, 0, 1, 3)
        self.gridLayout.addWidget(self.comboBox, 0, 2, 1, 1)
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)

        
        self.model = QtGui.QStandardItemModel(self)

        self.proxy = QtCore.QSortFilterProxyModel(self)
        self.proxy.setSourceModel(self.model)

        self.view.setModel(self.proxy)

        self.lineEdit.textChanged.connect(self.on_lineEdit_textChanged)
        self.comboBox.currentIndexChanged.connect(self.on_comboBox_currentIndexChanged)

        self.horizontalHeader = self.view.horizontalHeader()
        self.horizontalHeader.sectionClicked.connect(self.on_view_horizontalHeader_sectionClicked)

        self.retranslateUi()
        
    def retranslateUi(self):
        self.label.setText(QtWidgets.QApplication.translate("label", "正则过滤", None, -1))

        # NOTE 修改行名称
        header_list = [
            QtWidgets.QApplication.translate("header", "变量名", None, -1),
            QtWidgets.QApplication.translate("header", "变量值", None, -1),
        ]
        for column,label in enumerate(header_list):
            self.model.setHeaderData(column, QtCore.Qt.Horizontal,label)

        self.comboBox.clear()
        self.comboBox.addItems(header_list)
    
    def addItems(self,data):

        for var,val in data.items():
            var_item = QtGui.QStandardItem(str(var))
            var_item.setEditable(False)
            var_item.setToolTip(str(type(val)))


            val_item = QtGui.QStandardItem('"%s"' % val if type(val) == str else str(val))


            self.model.invisibleRootItem().appendRow([var_item,val_item])

        self.retranslateUi()

    def clearItems(self):
        for i in range(self.model.rowCount()):
            self.model.removeRows(i,self.model.rowCount())

    def setModel(self,model):
        self.model = model
        self.proxy.setSourceModel(self.model)

    @QtCore.Slot(int)
    def on_view_horizontalHeader_sectionClicked(self, logicalIndex):
        self.logicalIndex   = logicalIndex
        self.menuValues     = QtWidgets.QMenu(self)
        self.signalMapper   = QtCore.QSignalMapper(self)  

        self.comboBox.blockSignals(True)
        self.comboBox.setCurrentIndex(self.logicalIndex)
        self.comboBox.blockSignals(True)

        valuesUnique = [    self.model.item(row, self.logicalIndex).text()
                            for row in range(self.model.rowCount())
                            ]

        actionAll = QtWidgets.QAction("All", self)
        actionAll.triggered.connect(self.on_actionAll_triggered)
        self.menuValues.addAction(actionAll)
        self.menuValues.addSeparator()

        for actionNumber, actionName in enumerate(sorted(list(set(valuesUnique)))):              
            action = QtWidgets.QAction(actionName, self)
            self.signalMapper.setMapping(action, actionNumber)  
            action.triggered.connect(self.signalMapper.map)  
            self.menuValues.addAction(action)

        self.signalMapper.mapped.connect(self.on_signalMapper_mapped)  

        headerPos = self.view.mapToGlobal(self.horizontalHeader.pos())        

        posY = headerPos.y() + self.horizontalHeader.height()
        posX = headerPos.x() + self.horizontalHeader.sectionPosition(self.logicalIndex)

        self.menuValues.exec_(QtCore.QPoint(posX, posY))

    @QtCore.Slot()
    def on_actionAll_triggered(self):
        filterColumn = self.logicalIndex
        filterString = QtCore.QRegExp(  "",
                                        QtCore.Qt.CaseInsensitive,
                                        QtCore.QRegExp.RegExp
                                        )

        self.proxy.setFilterRegExp(filterString)
        self.proxy.setFilterKeyColumn(filterColumn)

    @QtCore.Slot(int)
    def on_signalMapper_mapped(self, i):
        stringAction = self.signalMapper.mapping(i).text()
        filterColumn = self.logicalIndex
        filterString = QtCore.QRegExp(  stringAction,
                                        QtCore.Qt.CaseSensitive,
                                        QtCore.QRegExp.FixedString
                                        )

        self.proxy.setFilterRegExp(filterString)
        self.proxy.setFilterKeyColumn(filterColumn)

    @QtCore.Slot(str)
    def on_lineEdit_textChanged(self, text):
        search = QtCore.QRegExp(    text,
                                    QtCore.Qt.CaseInsensitive,
                                    QtCore.QRegExp.RegExp
                                    )

        self.proxy.setFilterRegExp(search)

    @QtCore.Slot(int)
    def on_comboBox_currentIndexChanged(self, index):
        self.proxy.setFilterKeyColumn(index)

  

class Debugger_Info(QtWidgets.QWidget):
    def __init__(self):
        super(Debugger_Info,self).__init__()

        ui_path = os.path.join(DIR,"ui","debugVar.ui")
        loadUi(ui_path,self)
        
        self.filter_table = FilterTableWidget()

        data = {
            "a":'1',
            "b":2,
            "c":self.filter_table
        }
        self.filter_table.addItems(data)

        replaceWidget(self.Var_Table,self.filter_table)

        self.var_toggle_anim = CollapsibleWidget.install(self.Var_Toggle,self.filter_table)
        self.scope_toggle_anim = CollapsibleWidget.install(self.Scope_Toggle,self.Scope_List)
    
    def mayaShow(self):
        return mayaShow(self,"MPDB_Info")

class LinkPathLabel(QtWidgets.QLabel):
    
    def __init__(self,*args,**kwargs):
        super(LinkPathLabel,self).__init__(*args,**kwargs)
        self.linkActivated.connect(self.openPath)
        self.color = "yellow"
        self.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse|QtCore.Qt.LinksAccessibleByMouse)
        self.setWordWrap(True)

        font = self.font()
        font.setPointSize(12)
        font.setBold(True)
        self.setFont(font)

    def setText(self,path):
        self.path = path
        link = """
        <html><head/><body><p><a href="{path}"><span style=" text-decoration: underline; color:{color};">{path}</span></a></p></body></html>
        """.format(path=path,color=self.color)
        super(LinkPathLabel,self).setText(link)

    def openPath(self):
        if os.path.exists(self.path):
            os.startfile(self.path)
        else:
            title = QtWidgets.QApplication.translate("path", "警告", None, -1)
            msg = QtWidgets.QApplication.translate("path", "路径不存在", None, -1)
            QtWidgets.QMessageBox.warning(self,title,msg)


class Debugger_Panel(QtWidgets.QWidget):
    def __init__(self):
        super(Debugger_Panel,self).__init__()

        self.info_panel = Debugger_Info()

        topleft = QtWidgets.QFrame()
        topleft.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.editor = CodeEditor(self)
        self.editor_layout = QtWidgets.QVBoxLayout()

        path = r"F:\repo\mpdb\scripts\mpdb\ui\debugVr_ui.py"
        self.link = LinkPathLabel()
        self.link.setText(path)

        self.editor_layout.addWidget(self.link)
        self.editor_layout.addWidget(self.editor)
        self.editor_layout.setContentsMargins(0, 0, 0, 0)
        topleft.setLayout(self.editor_layout)

        self.splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
        self.splitter.addWidget(topleft)
        self.splitter.addWidget(self.info_panel)

        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.splitter)
        self.setLayout(layout)

    def mayaShow(self):
        return mayaShow(self,"MPDB_Panel")


# import sys
# MODULE = r"F:\repo\mpdb\scripts"
# if MODULE not in sys.path:
#     sys.path.append(MODULE)

# try:
        
#     import mpdb
#     reload(mpdb)

#     debugger_ui = mpdb.Debugger_Panel().mayaShow()
# except:
#     import traceback
#     traceback.print_exc()