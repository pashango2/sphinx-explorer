#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division, print_function, absolute_import, unicode_literals

from qtpy.QtCore import *
from qtpy.QtWidgets import *

from sphinx_explorer.property_widget import PropertyModel
from sphinx_explorer.util import python_venv
from sphinx_explorer.util.commander import commander
from ..pip_manager import PackageModel, PipListTask
from ..task import push_task


class LoadingLabel(QLabel):
    def __init__(self, parent=None):
        super(LoadingLabel, self).__init__(parent)
        self.setAlignment(Qt.AlignCenter)
        self.setText("Loading...")

        if parent:
            parent.installEventFilter(self)

    def eventFilter(self, _, evt):
        evt_type = evt.type()
        if evt_type == QEvent.Resize:
            size = evt.size()
            self.setGeometry(0, 0, size.width(), size.height())

        return False


# noinspection PyArgumentList
class PythonInterpreterWidget(QWidget):
    def __init__(self, parent=None):
        super(PythonInterpreterWidget, self).__init__(parent)
        self.property_model = None
        self.root_index = QModelIndex()

        self.package_tree_view = QTreeView(self)
        self.package_tree_view.setRootIsDecorated(False)

        self.v_layout = QVBoxLayout(self)
        self.layout = QFormLayout()
        self.v_layout.addLayout(self.layout)
        self.v_layout.addWidget(self.package_tree_view)

        self.setLayout(self.v_layout)

        self.control_dict = {}
        self.python_combo = None

        self.loading_label = LoadingLabel(self.package_tree_view)
        self.loading_label.hide()

    def setup(self, property_model, root_index):
        # type: (PropertyModel, QModelIndex) -> None
        self.property_model = property_model
        self.root_index = root_index

        for item in property_model.properties(root_index):
            control = item.value_type.control(None, self)
            control.set_value(item.value)
            self.control_dict[item.key] = control
            self.layout.addRow(item.text(), control)

        combo = self.control_dict["python"]
        combo.combo_box.currentIndexChanged.connect(self._on_interpreter_changed)
        self.python_combo = combo

        self._on_interpreter_changed(combo.currentIndex())

    @Slot(int)
    def _on_interpreter_changed(self, _):
        item = self.property_model.get("python", self.root_index)
        item.value_item.set_value(self.python_combo.value())

        venv_setting = self.python_combo.value()
        activate_command = python_venv.activate_command(venv_setting)
        pre_commander = commander.create_pre_commander(activate_command)

        self.loading_label.show()
        task = PipListTask(pre_commander)
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
