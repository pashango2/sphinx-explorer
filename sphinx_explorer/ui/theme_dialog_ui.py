# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'theme_dialog.ui'
#
# Created by: PyQt5 UI code generator 5.8.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(767, 729)
        self.verticalLayout = QtWidgets.QVBoxLayout(Dialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.list_view_theme = QtWidgets.QListView(Dialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.list_view_theme.sizePolicy().hasHeightForWidth())
        self.list_view_theme.setSizePolicy(sizePolicy)
        self.list_view_theme.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.list_view_theme.setResizeMode(QtWidgets.QListView.Adjust)
        self.list_view_theme.setLayoutMode(QtWidgets.QListView.SinglePass)
        self.list_view_theme.setViewMode(QtWidgets.QListView.ListMode)
        self.list_view_theme.setModelColumn(0)
        self.list_view_theme.setObjectName("list_view_theme")
        self.horizontalLayout.addWidget(self.list_view_theme)
        self.text_edit_preview = DescriptionWidget(Dialog)
        self.text_edit_preview.setObjectName("text_edit_preview")
        self.horizontalLayout.addWidget(self.text_edit_preview)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.buttonBox = QtWidgets.QDialogButtonBox(Dialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(Dialog)
        self.buttonBox.accepted.connect(Dialog.accept)
        self.buttonBox.rejected.connect(Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "HTML Theme"))

from sphinx_explorer.property_widget import DescriptionWidget
