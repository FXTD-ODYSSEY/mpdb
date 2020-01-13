# coding:utf-8

__author__ =  'timmyliang'
__email__ =  '820472580@qq.com'
__date__ = '2020-01-14 00:28:03'

# NOTE https://stackoverflow.com/questions/14068823/how-to-create-filters-for-qtableview-in-pyqt

import sys
from PySide2.QtGui import *
from PySide2.QtCore import *
from PySide2.QtWidgets import *

# from PyQt4 import QtCore, QtGui

class myWindow(QMainWindow):
    def __init__(self, parent=None):
        super(myWindow, self).__init__(parent)
        self.centralwidget  = QWidget(self)
        self.lineEdit       = QLineEdit(self.centralwidget)
        self.view           = QTableView(self.centralwidget)
        self.comboBox       = QComboBox(self.centralwidget)
        self.label          = QLabel(self.centralwidget)

        self.gridLayout = QGridLayout(self.centralwidget)
        self.gridLayout.addWidget(self.lineEdit, 0, 1, 1, 1)
        self.gridLayout.addWidget(self.view, 1, 0, 1, 3)
        self.gridLayout.addWidget(self.comboBox, 0, 2, 1, 1)
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)

        self.setCentralWidget(self.centralwidget)
        self.label.setText("Regex Filter")

        self.model = QStandardItemModel(self)

        for rowName in range(3) * 5:
            self.model.invisibleRootItem().appendRow(
                [   QStandardItem("row {0} col {1}".format(rowName, column))    
                    for column in range(3)
                    ]
                )

        self.proxy = QSortFilterProxyModel(self)
        self.proxy.setSourceModel(self.model)

        self.view.setModel(self.proxy)
        self.comboBox.addItems(["Column {0}".format(x) for x in range(self.model.columnCount())])

        self.lineEdit.textChanged.connect(self.on_lineEdit_textChanged)
        self.comboBox.currentIndexChanged.connect(self.on_comboBox_currentIndexChanged)

        self.horizontalHeader = self.view.horizontalHeader()
        self.horizontalHeader.sectionClicked.connect(self.on_view_horizontalHeader_sectionClicked)

    def on_view_horizontalHeader_sectionClicked(self, logicalIndex):
        self.logicalIndex   = logicalIndex
        self.menuValues     = QMenu(self)
        self.signalMapper   = QSignalMapper(self)  

        self.comboBox.blockSignals(True)
        self.comboBox.setCurrentIndex(self.logicalIndex)
        self.comboBox.blockSignals(True)

        valuesUnique = [    self.model.item(row, self.logicalIndex).text()
                            for row in range(self.model.rowCount())
                            ]

        actionAll = QAction("All", self)
        actionAll.triggered.connect(self.on_actionAll_triggered)
        self.menuValues.addAction(actionAll)
        self.menuValues.addSeparator()

        for actionNumber, actionName in enumerate(sorted(list(set(valuesUnique)))):              
            action = QAction(actionName, self)
            self.signalMapper.setMapping(action, actionNumber)  
            action.triggered.connect(self.signalMapper.map)  
            self.menuValues.addAction(action)

        self.signalMapper.mapped.connect(self.on_signalMapper_mapped)  

        headerPos = self.view.mapToGlobal(self.horizontalHeader.pos())        

        posY = headerPos.y() + self.horizontalHeader.height()
        posX = headerPos.x() + self.horizontalHeader.sectionPosition(self.logicalIndex)

        self.menuValues.exec_(QPoint(posX, posY))

    def on_actionAll_triggered(self):
        filterColumn = self.logicalIndex
        filterString = QRegExp(  "",
                                        Qt.CaseInsensitive,
                                        QRegExp.RegExp
                                        )

        self.proxy.setFilterRegExp(filterString)
        self.proxy.setFilterKeyColumn(filterColumn)

    def on_signalMapper_mapped(self, i):
        stringAction = self.signalMapper.mapping(i).text()
        filterColumn = self.logicalIndex
        filterString = QRegExp(  stringAction,
                                        Qt.CaseSensitive,
                                        QRegExp.FixedString
                                        )

        self.proxy.setFilterRegExp(filterString)
        self.proxy.setFilterKeyColumn(filterColumn)

    def on_lineEdit_textChanged(self, text):
        search = QRegExp(    text,
                                    Qt.CaseInsensitive,
                                    QRegExp.RegExp
                                    )

        self.proxy.setFilterRegExp(search)

    def on_comboBox_currentIndexChanged(self, index):
        self.proxy.setFilterKeyColumn(index)


if __name__ == "__main__":
    import sys

    app  = QApplication(sys.argv)
    main = myWindow()
    main.show()
    main.resize(400, 600)
    sys.exit(app.exec_())