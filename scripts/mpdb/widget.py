# coding:utf-8

__author__ =  'timmyliang'
__email__ =  '820472580@qq.com'
__date__ = '2020-01-05 22:10:22'

"""

"""


from PySide2 import QtGui
from PySide2 import QtCore
from PySide2 import QtWidgets

class Debugger_UI(QtWidgets.QWidget):
    def __init__(self):
        super(Debugger_UI,self).__init__()

        layout = self.QHBoxLayout()
        self.setLayout(layout)

        
