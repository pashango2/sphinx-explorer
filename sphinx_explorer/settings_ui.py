# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/toshiyuki/sphinx-explorer/sphinx_explorer/settings.ui'
#
# Created: Wed Apr 19 20:20:52 2017
#      by: pyside-uic 0.2.15 running on PySide 1.2.4
#
# WARNING! All changes made in this file will be lost!

from qtpy import QtCore, QtGui

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(795, 385)
        self.verticalLayout_2 = QtGui.QVBoxLayout(Form)
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.button_open_home_dir = QtGui.QToolButton(Form)
        self.button_open_home_dir.setToolButtonStyle(QtCore.Qt.ToolButtonTextBesideIcon)
        self.button_open_home_dir.setObjectName("button_open_home_dir")
        self.horizontalLayout.addWidget(self.button_open_home_dir)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.verticalLayout_2.addLayout(self.horizontalLayout)
        self.splitter = QtGui.QSplitter(Form)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.splitter.sizePolicy().hasHeightForWidth())
        self.splitter.setSizePolicy(sizePolicy)
        self.splitter.setOrientation(QtCore.Qt.Horizontal)
        self.splitter.setObjectName("splitter")
        self.tree_view_category = QtGui.QTreeView(self.splitter)
        self.tree_view_category.setRootIsDecorated(True)
        self.tree_view_category.setObjectName("tree_view_category")
        self.tree_view_category.header().setVisible(False)
        self.stacked_widget = QtGui.QStackedWidget(self.splitter)
        self.stacked_widget.setFrameShape(QtGui.QFrame.NoFrame)
        self.stacked_widget.setFrameShadow(QtGui.QFrame.Plain)
        self.stacked_widget.setObjectName("stacked_widget")
        self.page = QtGui.QWidget()
        self.page.setObjectName("page")
        self.verticalLayout = QtGui.QVBoxLayout(self.page)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.property_widget = PropertyWidget(self.page)
        self.property_widget.setObjectName("property_widget")
        self.verticalLayout.addWidget(self.property_widget)
        self.stacked_widget.addWidget(self.page)
        self.page_2 = QtGui.QWidget()
        self.page_2.setObjectName("page_2")
        self.stacked_widget.addWidget(self.page_2)
        self.verticalLayout_2.addWidget(self.splitter)

        self.retranslateUi(Form)
        self.stacked_widget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(Form)
        Form.setTabOrder(self.tree_view_category, self.property_widget)
        Form.setTabOrder(self.property_widget, self.button_open_home_dir)

    def retranslateUi(self, Form):
        Form.setWindowTitle(QtGui.QApplication.translate("Form", "Form", None, QtGui.QApplication.UnicodeUTF8))
        self.button_open_home_dir.setText(QtGui.QApplication.translate("Form", "Open Setting Directory", None, QtGui.QApplication.UnicodeUTF8))

from .property_widget import PropertyWidget
