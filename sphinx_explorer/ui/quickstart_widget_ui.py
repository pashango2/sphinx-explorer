# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/toshiyuki/sphinx-explorer/sphinx_explorer/ui/quickstart_widget.ui'
#
# Created: Fri Apr 21 20:45:05 2017
#      by: pyside-uic 0.2.15 running on PySide 1.2.4
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(837, 639)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Form.sizePolicy().hasHeightForWidth())
        Form.setSizePolicy(sizePolicy)
        self.horizontalLayout = QtGui.QHBoxLayout(Form)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.splitter = QtGui.QSplitter(Form)
        self.splitter.setOrientation(QtCore.Qt.Horizontal)
        self.splitter.setObjectName("splitter")
        self.verticalLayoutWidget = QtGui.QWidget(self.splitter)
        self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")
        self.verticalLayout = QtGui.QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.property_widget = PropertyWidget(self.verticalLayoutWidget)
        self.property_widget.setObjectName("property_widget")
        self.verticalLayout.addWidget(self.property_widget)
        self.button_create_project = QtGui.QPushButton(self.verticalLayoutWidget)
        self.button_create_project.setMinimumSize(QtCore.QSize(0, 80))
        self.button_create_project.setObjectName("button_create_project")
        self.verticalLayout.addWidget(self.button_create_project)
        self.output_widget = QConsoleWidget(self.splitter)
        self.output_widget.setObjectName("output_widget")
        self.horizontalLayout.addWidget(self.splitter)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        Form.setWindowTitle(QtGui.QApplication.translate("Form", "Form", None, QtGui.QApplication.UnicodeUTF8))
        self.button_create_project.setText(QtGui.QApplication.translate("Form", "Create Project", None, QtGui.QApplication.UnicodeUTF8))

from .util.QConsoleWidget import QConsoleWidget
from .property_widget import PropertyWidget
