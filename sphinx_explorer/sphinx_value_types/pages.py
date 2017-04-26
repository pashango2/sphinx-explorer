#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division, print_function, absolute_import, unicode_literals
from qtpy.QtCore import *
from qtpy.QtGui import *
from qtpy.QtWidgets import *

from ..pip_manager import PackageModel, PipListTask
from ..task import push_task

import os
from sphinx_explorer.property_widget import PropertyModel
from sphinx_explorer.property_widget import cog_icon
from sphinx_explorer.property_widget.widgets import MovableListWidget
from sphinx_explorer.util.python_venv import check_python_version, VenvSetting


class LoadingLabel(QLabel):
    def __init__(self, parent=None):
        super(LoadingLabel, self).__init__(parent)
        self.setAlignment(Qt.AlignCenter)
        self.setText("Loading...")

        if parent:
            parent.installEventFilter(self)

    def eventFilter(self, obj, evt):
        evt_type = evt.type()
        if evt_type == QEvent.Resize:
            size = evt.size()
            self.setGeometry(0, 0, size.width(), size.height())

        return False


class PythonInterpreterWidget(QWidget):
    def __init__(self, parent=None):
        super(PythonInterpreterWidget, self).__init__(parent)
        self.property_model = None
        self.root_index = QModelIndex()

        self.package_tree_view = QTreeView(self)
        self.package_tree_view.setRootIsDecorated(False)

        self.v_layout = QVBoxLayout(self)
        self.layout = QFormLayout(self)
        self.v_layout.addLayout(self.layout)
        self.v_layout.addWidget(self.package_tree_view)

        self.setLayout(self.v_layout)

        self.control_dict = {}

        self.loading_label = LoadingLabel(self.package_tree_view)
        self.loading_label.hide()

    def setup(self, property_model, root_index):
        # type: (PropertyModel, QModelIndex) -> None

        for item in property_model.properties(root_index):
            control = item.value_type.control(None, self)
            self.control_dict[item.key] = control
            self.layout.addRow(item.text(), control)

        combo = self.control_dict["python"]
        combo.combo_box.currentIndexChanged.connect(self._on_interpreter_changed)

        self._on_interpreter_changed(combo.currentIndex())

    @Slot(int)
    def _on_interpreter_changed(self, idx):
        self.loading_label.show()
        task = PipListTask()
        task.finished.connect(self._on_package_load_finished)
        push_task(task)

    @Slot(list)
    def _on_package_load_finished(self, packages):
        model = PackageModel(self)
        model.load(packages)
        self.package_tree_view.setModel(model)
        self.package_tree_view.resizeColumnToContents(0)
        self.loading_label.hide()

    def teardown(self):
        pass
