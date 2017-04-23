#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division, print_function, absolute_import, unicode_literals
from qtpy.QtWidgets import *
from .pip_manager import PackageModel
from .plugin import extension


# noinspection PyArgumentList
class PackageManagerDlg(QDialog):
    def __init__(self, package_model, parent=None):
        # type: (PackageModel, QWidget) -> None
        super(PackageManagerDlg, self).__init__(parent)
        self.package_model = package_model

        self.tree_view = QTreeView(self)
        self.tree_view.setRootIsDecorated(False)

        self.filter_model = self.package_model.create_filter_model(
            extension.dependent_packages(),
            parent=self,
        )
        self.tree_view.setModel(self.filter_model)

        layout = QVBoxLayout(self)
        layout.addWidget(self.tree_view)
        self.setLayout(layout)

        self.setWindowTitle(self.tr("Package Manager"))
