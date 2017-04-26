# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/toshiyuki/program/sphinx-explorer/sphinx_explorer/ui/settings.ui'
#
# Created by: PyQt5 UI code generator 5.8.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(795, 385)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(Form)
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.splitter = QtWidgets.QSplitter(Form)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.splitter.sizePolicy().hasHeightForWidth())
        self.splitter.setSizePolicy(sizePolicy)
        self.splitter.setOrientation(QtCore.Qt.Horizontal)
        self.splitter.setObjectName("splitter")
        self.tree_view_category = QtWidgets.QTreeView(self.splitter)
        self.tree_view_category.setRootIsDecorated(True)
        self.tree_view_category.setObjectName("tree_view_category")
        self.tree_view_category.header().setVisible(False)
        self.stacked_widget = QtWidgets.QStackedWidget(self.splitter)
        self.stacked_widget.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.stacked_widget.setFrameShadow(QtWidgets.QFrame.Plain)
        self.stacked_widget.setObjectName("stacked_widget")
        self.page = QtWidgets.QWidget()
        self.page.setObjectName("page")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.page)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.property_widget = PropertyWidget(self.page)
        self.property_widget.setObjectName("property_widget")
        self.verticalLayout.addWidget(self.property_widget)
        self.stacked_widget.addWidget(self.page)
        self.page_2 = QtWidgets.QWidget()
        self.page_2.setObjectName("page_2")
        self.stacked_widget.addWidget(self.page_2)
        self.verticalLayout_2.addWidget(self.splitter)

        self.retranslateUi(Form)
        self.stacked_widget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(Form)
        Form.setTabOrder(self.tree_view_category, self.property_widget)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))

from ..property_widget import PropertyWidget
