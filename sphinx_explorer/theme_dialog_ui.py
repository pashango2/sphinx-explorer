# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/toshiyuki/sphinx-explorer/sphinx_explorer/theme_dialog.ui'
#
# Created: Fri Apr 14 08:03:24 2017
#      by: pyside-uic 0.2.15 running on PySide 1.2.4
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(767, 729)
        self.verticalLayout = QtGui.QVBoxLayout(Dialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.list_view_theme = QtGui.QListView(Dialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.list_view_theme.sizePolicy().hasHeightForWidth())
        self.list_view_theme.setSizePolicy(sizePolicy)
        self.list_view_theme.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        self.list_view_theme.setResizeMode(QtGui.QListView.Adjust)
        self.list_view_theme.setLayoutMode(QtGui.QListView.SinglePass)
        self.list_view_theme.setViewMode(QtGui.QListView.ListMode)
        self.list_view_theme.setModelColumn(0)
        self.list_view_theme.setObjectName("list_view_theme")
        self.horizontalLayout.addWidget(self.list_view_theme)
        self.text_edit_preview = DescriptionWidget(Dialog)
        self.text_edit_preview.setObjectName("text_edit_preview")
        self.horizontalLayout.addWidget(self.text_edit_preview)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.buttonBox = QtGui.QDialogButtonBox(Dialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(Dialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("accepted()"), Dialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("rejected()"), Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QtGui.QApplication.translate("Dialog", "HTML Theme", None, QtGui.QApplication.UnicodeUTF8))

from sphinx_explorer.property_widget import DescriptionWidget
