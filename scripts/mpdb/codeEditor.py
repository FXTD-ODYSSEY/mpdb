#!/usr/bin/python3
# -*- coding: utf-8 -*-

# NOTE https://stackoverflow.com/questions/40386194/create-text-area-textedit-with-line-number-in-pyqt
import os
import re
import sys
import keyword
from textwrap import  dedent

from maya import cmds
from maya import OpenMayaUI

from PySide2 import QtGui
from PySide2 import QtCore
from PySide2 import QtWidgets
from PySide2.QtCore import Qt, QRect, QSize,QRegExp
from PySide2.QtWidgets import QWidget, QPlainTextEdit, QTextEdit,QVBoxLayout
from PySide2.QtGui import QColor, QPainter, QTextFormat,QTextCharFormat,QFont,QSyntaxHighlighter

from Qt.QtCompat import wrapInstance

# from PySide2.QtGui import *
# from PySide2.QtCore import *
# from PySide2.QtWidgets import *
LINEBAR_COLOR = QColor("#444444")
LINE_COLOR = QColor("dark")
LINE_MARGIN = 5
LINEBAR_NUM_COLOR = QColor("yellow")
LINEBAR_BP_COLOR = QColor("red")


class Highlighter(QSyntaxHighlighter):
    """syntax highlighter"""
    def __init__(self, parent=None):
        super(Highlighter, self).__init__(parent)

        self.__rules = []
        
        # numeric color
        self._numericFormat = QTextCharFormat()
        self._numericFormat.setForeground(QColor('#9ACD32'))
        
        # mel command options started with -
        melOpsFormat = QTextCharFormat()
        melOpsFormat.setForeground(QColor('#B8860B'))
        self.__rules.append((re.compile('-[a-zA-Z]+\\b'), melOpsFormat))

        # keywords color
        self._keywordColor = QColor(0, 128, 255)

        self._numeric()
        self._keywordFormat()
        self._cmdsFunctionFormat()

        # maya api format
        mapiFormat = QTextCharFormat()
        mapiFormat.setForeground(self._keywordColor)
        self.__rules.append((re.compile('\\bM\\w+\\b'), mapiFormat))
        # Qt
        self.__rules.append((re.compile('\\bQ\\w+\\b'), mapiFormat))

        # quotation
        self._quotationFormat = QTextCharFormat()
        self._quotationFormat.setForeground(Qt.green)
        # quote: ""
        self.__rules.append((re.compile('".*"'), self._quotationFormat))
        # single quotes for python: ''
        self.__rules.append((re.compile("'.*'"), self._quotationFormat))

        # sing line comment
        self._commentFormat = QTextCharFormat()
        # orange red
        self._commentFormat.setForeground(QColor(255, 128, 64))
        # // mel comment
        self.__rules.append((re.compile('//[^\n]*'), self._commentFormat))
        # # python comment
        self.__rules.append((re.compile('#[^\n]*'), self._commentFormat))

        # function and class format
        funcFormat = QTextCharFormat()
        funcFormat.setFontWeight(QFont.Bold)
        self.__rules.append((re.compile('\\b(\\w+)\(.*\):'), funcFormat))

        # mel warning
        warningFormat = QTextCharFormat()
        warningFormat.setForeground(QColor('#FF9ACD32'))
        warningFormat.setBackground(Qt.yellow)
        warningFormat.setFontWeight(QFont.Bold)
        self.__rules.append((re.compile('// Warning:[^\n]*//'), warningFormat))

        # mel error
        errorFormat = QTextCharFormat()
        errorFormat.setForeground(QColor('#FF9ACD32'))
        errorFormat.setBackground(Qt.red)
        errorFormat.setFontWeight(QFont.Bold)
        self.__rules.append((re.compile('// Error:[^\n]*//'), errorFormat))

        # Quotes
        self._singleQuotes = QRegExp("'''")
        self._doubleQuotes = QRegExp('"""')

        # mel multi-line comment: /*  */
        self._melMLComStart = re.compile('/\\*')
        self._melMLComEnd = re.compile('\\*/')
        
    def _numeric(self):
        '''set up numeric format'''
        num_01 = re.compile('\\b[+-]?[0-9]+[lL]?\\b')
        num_02 = re.compile('\\b[+-]?0[xX][0-9A-Fa-f]+[lL]?\\b')
        num_03 = re.compile('\\b[+-]?[0-9]+(?:\.[0-9]+)?(?:[eE][+-]?[0-9]+)?\\b')
        num_regs = (num_01, num_02, num_03)
        for nr in num_regs:
            self.__rules.append((nr, self._numericFormat))

    def _keywordFormat(self):
        '''set up keyword format'''
        # mel keyword
        melKeywords = ['false', 'float', 'int', 'matrix', 'off', 'on', 'string',
                       'true', 'vector', 'yes', 'alias', 'case', 'catch', 'break',
                       'case', 'continue', 'default', 'do', 'else', 'for', 'if', 'in',
                       'while', 'alias', 'case', 'catch', 'global', 'proc', 'return', 'source', 'switch']
        # python keyword
        pyKeywords = keyword.kwlist + ['False', 'True', 'None']

        keywords = {}.fromkeys(melKeywords)
        keywords.update({}.fromkeys(pyKeywords))
        # keyword format
        keywordFormat = QTextCharFormat()
        keywordFormat.setForeground(self._keywordColor)
        keywordFormat.setFontWeight(QFont.Bold)
        kwtext = '\\b(' + "|".join(keywords) + ')\\b'
        self.__rules.append((re.compile(kwtext), keywordFormat))

    def _cmdsFunctionFormat(self):
        '''set up maya.cmds functions'''
        mayaBinDir = os.path.dirname(sys.executable)
        cmdsList = os.path.join(mayaBinDir, 'commandList')
        functions = '\\b('
        with open(cmdsList) as phile:
            for line in phile:
                functions += line.split(' ')[0] + '|'

        # global MEL procedures
        melProcedures = cmds.melInfo()
        maxlen = 1400
        stop = len(melProcedures) / maxlen
        melProc = []
        melProc.append('\\b(' + '|'.join(melProcedures[:maxlen]) + ')\\b')
        for i in range(1, stop - 1):
            start = maxlen * i
            end = maxlen * (i + 1)
            melProc.append('\\b(' + '|'.join(melProcedures[start:end]) + ')\\b')
        melProc.append('\\b(' + '|'.join(melProcedures[maxlen*stop:]) + ')\\b')

        # TODO: should update it when a plug-in was load.
        # function from plug-ins
        plugins = cmds.pluginInfo(q=1, listPlugins=1)
        for plugin in plugins:
            funcFromPlugin = cmds.pluginInfo(plugin, q=1, command=1)
            if funcFromPlugin:
                functions += '|'.join(funcFromPlugin)
        functions = functions[:-1] + ')\\b'

        # function format
        funcFormat = QTextCharFormat()
        funcFormat.setForeground(self._keywordColor)
        self.__rules.append((re.compile(functions), funcFormat))
        for mp in melProc:
            self.__rules.append((re.compile(mp), funcFormat))

    def _melMLCommentFormat(self, text):
        '''set up mel multi-line comment: /*  */'''
        startIndex = 0
        commentLen = 0
        self.setCurrentBlockState(0)
        if self.previousBlockState() != 1:
            searchStart = self._melMLComStart.search(text)
            if searchStart:
                startIndex = searchStart.start()
                searchEnd = self._melMLComEnd.search(text)
                if searchEnd:
                    commentLen = searchEnd.end() - startIndex
                else:
                    self.setCurrentBlockState(1)
                    commentLen = len(text) - startIndex
        else:
            searchEnd = self._melMLComEnd.search(text)
            if searchEnd:
                commentLen = searchEnd.end()
            else:
                self.setCurrentBlockState(1)
                commentLen = len(text)
        if commentLen > 0:
            self.setFormat(startIndex, commentLen, self._commentFormat)
            
    def quotesFormat(self, text, regExp, state):
        '''set up single or double quotes strings format'''
        if self.previousBlockState() == state:
            startIndex = 0
            add = 0
        else:
            startIndex = regExp.indexIn(text)
            add = regExp.matchedLength()
            
        while startIndex >= 0:
            end = regExp.indexIn(text, startIndex + add)
            if end >= add:
                quotesLen = end - startIndex + regExp.matchedLength()
                self.setCurrentBlockState(0)
            else:
                self.setCurrentBlockState(state)
                quotesLen = len(text) - startIndex + add
            self.setFormat(startIndex, quotesLen, self._quotationFormat)
            startIndex = regExp.indexIn(text, startIndex + quotesLen)
            
        if self.currentBlockState() == state:
            return True
        else:
            return False

    def highlightBlock(self, text):
        '''highlight text'''
        for regExp, tformat in self.__rules:
            match = regExp.search(text)
            while match:
                self.setFormat(match.start(), match.end() - match.start(), tformat)
                match = regExp.search(text, match.end())

        # blocks
        self._melMLCommentFormat(text)
        quotesState = self.quotesFormat(text, self._singleQuotes, 2)
        if not quotesState:
            self.quotesFormat(text, self._doubleQuotes, 3)


class QLineNumberArea(QWidget):
    def __init__(self, parent = None):
        super(QLineNumberArea, self).__init__(parent)
        self.fixWidth = 10
        self.paintLineNum = -1
        self.current_line = -1

        self.editor = parent
        layout = QVBoxLayout()
        self.setLayout(layout)
        self.editor.blockCountChanged.connect(self.update_width)
        self.editor.updateRequest.connect(self.update_on_scroll)
        self.update_width('1')

    def paintLine(self,num):
        self.paintLineNum = num

    def update_on_scroll(self, rect, scroll):
        if self.isVisible():
            if scroll:
                self.scroll(0, scroll)
            else:
                self.update()

    def update_width(self, string):
        width = self.fontMetrics().width(str(string)) + self.fixWidth
        if self.width() != width:
            self.setFixedWidth(width)

    def paintEvent(self, event):
        if self.isVisible():
            block = self.editor.firstVisibleBlock()
            height = self.fontMetrics().height()
            number = block.blockNumber()
            painter = QPainter(self)
            painter.fillRect(event.rect(), LINEBAR_COLOR)
            painter.drawRect(event.rect().width()-1, 0, event.rect().width(), event.rect().height() - 1)
            font = painter.font()
            current_block = self.editor.textCursor().block().blockNumber() + 1

            condition = True
            while block.isValid() and condition:
                block_geometry = self.editor.blockBoundingGeometry(block)
                offset = self.editor.contentOffset()
                block_top = block_geometry.translated(offset).top()
                number += 1

                # NOTE set the linebar breakpoint color
                if self.paintLineNum > 0 and number == self.paintLineNum:
                    font.setBold(True)
                    block_rect = QRect(LINE_MARGIN, block_top, self.width() - LINE_MARGIN*2, height)
                    painter.fillRect(block_rect, LINEBAR_BP_COLOR)
                # NOTE set the current line color
                elif number == current_block:
                    font.setBold(True)
                    block_rect = QRect(LINE_MARGIN, block_top, self.width() - LINE_MARGIN*2, height)
                    painter.fillRect(block_rect, LINEBAR_NUM_COLOR)
                else:
                    font.setBold(False)

                painter.setFont(font)
                rect = QRect(0, block_top, self.width() - 5, height)
                painter.drawText(rect, Qt.AlignRight, '%i'%number)

                if block_top > event.rect().bottom():
                    condition = False

                block = block.next()

            painter.end()
    
    def contextMenuEvent(self, event):
        self.menu = QtWidgets.QMenu(self)
        goto_action = QtWidgets.QAction('Goto Line', self)

        goto_action.triggered.connect(self.gotoLine)
        self.menu.addAction(goto_action)
        pos = QtGui.QCursor.pos()
        self.menu.popup(pos)

    def gotoLine(self):
        # current_line = self.editor.textCursor().block().blockNumber() + 1
        self.editor.paintLine(self.current_line)
        print "gotoLine",self.current_line

    def mousePressEvent(self,event):
        self.current_line = self.currentCursorLineNum()
        self.editor.setCurrentLine(self.current_line)
        
    def currentCursorLineNum(self):
        # NOTE calculate the current click number
        pos = QtGui.QCursor.pos()
        local_pos = self.mapFromGlobal(pos)
        
        document = self.editor.document()

        metrics = self.editor.fontMetrics()

        # NOTE 使用 Courier New 字体需要 加 1
        height = metrics.height() + 1 
        offset = self.editor.contentOffset()
        bar = self.editor.verticalScrollBar()
        initial_height = (bar.value()+1)*height

        num = int((local_pos.y()+offset.y()+initial_height)/height)
        max_line = document.lineCount()
        if num > max_line:
            num = max_line
        return num




class CodeEditor(QPlainTextEdit):
    def __init__(self, parent=None):
        super(CodeEditor,self).__init__(parent)
        self.lineNumberArea = QLineNumberArea(self)
        self.blockCountChanged.connect(self.updateLineNumberAreaWidth)
        self.updateRequest.connect(self.updateLineNumberArea)
        # self.cursorPositionChanged.connect(self.highlightCurrentLine)

        # NOTE 使用 Courier New 字体解决缩进问题
        document = self.document()
        font = document.defaultFont()
        font.setFamily("Courier New,Microsoft YaHei UI")
        document.setDefaultFont(font)

        self.updateLineNumberAreaWidth(5)
        highlighter = Highlighter(parent=self)
        highlighter.setDocument(document)
        
        self.setReadOnly(True)
        self.setWordWrapMode(QtGui.QTextOption.NoWrap)
        self.paintLineNum = -1

        self.installEventFilter(self)

        # TODO test code
        self.setPlainText(dedent("""
# coding:utf-8

__author__ =  'timmyliang'
__email__ =  '820472580@qq.com'
__date__ = '2020-01-05 21:57:02'


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


def mayaToQT(name):
 
    ptr = OpenMayaUI.MQtUtil.findControl( name )
    if ptr is None:         
        ptr = OpenMayaUI.MQtUtil.findLayout( name )    
    if ptr is None:         
        ptr = OpenMayaUI.MQtUtil.findMenuItem( name )
    if ptr is not None:     
        return wrapInstance( long( ptr ), QtWidgets.QWidget )


def qtToMaya(widget):

    return OpenMayaUI.MQtUtil.fullName(
        long(
            getCppPointer(widget)[0]
        ) 
    )


# ----------------------------------------------------------------------------


def getStatusLine():
    gStatusLine = mel.eval("$tmpVar=$gStatusLine")
    return mayaToQT(gStatusLine)

def mayaWindow():

    window = OpenMayaUI.MQtUtil.mainWindow()
    window = wrapInstance(long(window), QtWidgets.QMainWindow)
    
    return window

# ----------------------------------------------------------------------------

def createUIComponentToolBar(ControlName="CustomToolBar"):
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

        """))
        self.paintLine(66)

    def eventFilter(self, reciever, event):
        # NOTE 如果 focus 窗口， 阻断键盘输入
        if event.type() == QtCore.QEvent.KeyPress and self.hasFocus():
            return True
        return False   
        

    def lineNumberAreaWidth(self):
        digits = 1
        max_value = max(1, self.blockCount())
        while max_value >= 10:
            max_value /= 10
            digits += 1
        space = self.lineNumberArea.fixWidth + self.fontMetrics().width('9') * digits
        return space

    def updateLineNumberAreaWidth(self, _):
        self.setViewportMargins(self.lineNumberAreaWidth(), 0, 0, 0)

    def updateLineNumberArea(self, rect, dy):
        if dy:
            self.lineNumberArea.scroll(0, dy)
        else:
            self.lineNumberArea.update(0, rect.y(), self.lineNumberArea.width(), rect.height())
        if rect.contains(self.viewport().rect()):
            self.updateLineNumberAreaWidth(0)

    def resizeEvent(self, event):
        super(CodeEditor,self).resizeEvent(event)
        cr = self.contentsRect()
        self.lineNumberArea.setGeometry(QRect(cr.left(), cr.top(), self.lineNumberAreaWidth(), cr.height()))

    def paintEvent(self, event):
        if self.isVisible() and self.paintLineNum > 0:

            # # TODO 触发resize事件 更新背景
            # self.resize(self.width(),self.height()+1)
            # self.resize(self.width(),self.height()-1)
            # NOTE 更新绘制
            self.viewport().update()

            block = self.firstVisibleBlock()
            height = self.lineNumberArea.fontMetrics().height()
            number = block.blockNumber()
            painter = QPainter(self.viewport())
            
            condition = True
            while block.isValid() and condition:
                block_geometry = self.blockBoundingGeometry(block)
                offset = self.contentOffset()
                block_top = block_geometry.translated(offset).top()
                number += 1
                
                block_rect = QRect(0, block_top, self.width(), height)
                
                if number == self.paintLineNum:
                    lineColor = QColor(LINE_COLOR).lighter(100)
                    painter.fillRect(block_rect, lineColor)
                    painter.drawRect(block_rect)
                    condition = False
        
                if block_top > event.rect().bottom():
                    condition = False
                    
                block = block.next()

            painter.end()
        return super(CodeEditor,self).paintEvent(event)
        
    def paintLine(self,num):
        self.paintLineNum = num
        self.lineNumberArea.paintLine(num)
        self.setCurrentLine(num)
    
    def setCurrentLine(self,num):
        # NOTE Jump Cursor 
        document = self.document()
        block = document.findBlockByLineNumber(num-1)
        cursor = QtGui.QTextCursor(block)
        self.setTextCursor(cursor)

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


if __name__ == '__main__':

    codeEditor = CodeEditor()
    codeEditor.mayaShow()


# import sys
# MODULE = r"F:\repo\mpdb\scripts"
# if MODULE not in sys.path:
#     sys.path.append(MODULE)

# try:
        
#     import mpdb
#     reload(mpdb)

#     debugger_ui = mpdb.CodeEditor().mayaShow()
# except:
#     import traceback
#     traceback.print_exc()