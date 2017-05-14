#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division, print_function, absolute_import, unicode_literals

from qtpy.QtCore import *
from qtpy.QtGui import *
from qtpy.QtWidgets import *


class ExtensionTreeWidget(QTreeWidget):
    def __init__(self, parent=None):
        super(ExtensionTreeWidget, self).__init__(parent)
        self.setHeaderHidden(True)
        self.setRootIsDecorated(False)

    def addExtension(self, name):
        item = QTreeWidgetItem()
        widget = ExtensionWidget(self)
        widget.setup(name, "", "toshi")

        self.addTopLevelItem(item)
        self.setItemWidget(item, 0, widget)


# noinspection PyArgumentList
class ExtensionWidget(QWidget):
    def __init__(self, parent=None):
        super(ExtensionWidget, self).__init__(parent)

        self.frame = QFrame(self)

        self.layout = QVBoxLayout()
        self.name = QLabel("Name", self)
        self.description = QLabel("Description", self)
        self.author = QLabel("Author", self)
        self.uninstall_button = QPushButton("UnInstall", self)
        self.disable_button = QPushButton("Disable", self)

        self.author.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Fixed
        )

        self.layout.addWidget(self.name)
        self.layout.addWidget(self.description)

        self.h_layout = QHBoxLayout()
        self.h_layout.addWidget(self.author)
        self.h_layout.addWidget(self.uninstall_button)
        self.h_layout.addWidget(self.disable_button)

        self.layout.addLayout(self.h_layout)

        self.frame.setLayout(self.layout)
        self.frame.setStyleSheet("QFrame{border-radius: 15px; padding: 4px;}")

        layout = QVBoxLayout()
        layout.addWidget(self.frame)
        layout.setContentsMargins(8, 4, 8, 4)
        self.setLayout(layout)

    def setup(self, name, description, author):
        self.name.setText(name)
        self.description.setText(description)
        self.author.setText(author)


def main():
    import sys

    app = QApplication(sys.argv)

    widget = ExtensionTreeWidget()
    widget.addExtension("test")
    widget.addExtension("test2")

    widget.show()

    app.exec_()


if __name__ == "__main__":
    main()
