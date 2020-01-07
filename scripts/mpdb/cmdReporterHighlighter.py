# -*- coding: UTF-8 -*-

# The MIT License (MIT)
#
# Copyright (c) 2014-2018 Mack Stone
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of
# this software and associated documentation files (the "Software"), to deal in
# the Software without restriction, including without limitation the rights to
# use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
# the Software, and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
# FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
# COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
# IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

# How to use it
# open script editor and run
#
# import cmdReporterHighlighter as crHighlighter
# crHighlighter.highlightCmdReporter()
#
# using userSetup.py
# added follow line to your userSetup.py
#
# from maya import utils
# import cmdReporterHighlighter as crHighlighter
# utils.executeDeferred(crHighlighter.launchFromCmdWndIcon)

import sys
import os
import re
import keyword

from maya import (cmds, mel)
from maya import OpenMayaUI as omui

try:
  from PySide2.QtCore import * 
  from PySide2.QtGui import * 
  from PySide2.QtWidgets import *
  from PySide2 import __version__
  from shiboken2 import wrapInstance 
except ImportError:
  from PySide.QtCore import * 
  from PySide.QtGui import * 
  from PySide import __version__
  from shiboken import wrapInstance 

def launchFromCmdWndIcon():
    '''launch from maya command line script editor icon.'''
    def cmdWnd(arg=None):
        cmds.ScriptEditor()
        highlightCmdReporter()

    # get command line formLayout
    gCommandLineForm = mel.eval('$tempVar = $gCommandLineForm')
    commandLineForm = cmds.formLayout(gCommandLineForm, q=1, ca=1)[0]
    # get cmdWndIcon button
    cmdWndIcon = cmds.formLayout(commandLineForm, q=1, ca=1)[-1]
    # change the command of the button
    cmds.symbolButton(cmdWndIcon, e=1, c=cmdWnd)

    # change the main manu item command
    #menuName = 'wmScriptEditor'
    #if cmds.menuItem(menuName, q=1, ex=1):
        #cmds.menuItem(menuName, e=1, c=cmdWnd)

def getMayaWindowWidget():
    '''get maya window widget for Qt'''
    mwin = None
    try:
        from shiboken import wrapInstance
        mwinPtr = omui.MQtUtil.mainWindow()
        mwin = wrapInstance(long(mwinPtr), QMainWindow)
    except:
        mapp = QApplication.instance()
        for widget in mapp.topLevelWidgets():
            if widget.objectName() == 'MayaWindow':
                mwin = widget
                break
    return mwin

def highlightCmdReporter():
    '''find cmdScrollFieldReporter and highlight it'''
    mwin = getMayaWindowWidget()
    cmdReporters = cmds.lsUI(type='cmdScrollFieldReporter')
    if not cmdReporters: return
    # only setup for the first one
    cmdReporter = mwin.findChild(QTextEdit, cmdReporters[0])
    highlighter = Highlighter(parent=mwin)
    highlighter.setDocument(cmdReporter.document())

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