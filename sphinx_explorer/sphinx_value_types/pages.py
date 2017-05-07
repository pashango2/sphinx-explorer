#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division, print_function, absolute_import, unicode_literals

from qtpy.QtCore import *
from qtpy.QtWidgets import *

from sphinx_explorer.python_venv import PipInstallTask
from sphinx_explorer.property_widget import PropertyModel
from sphinx_explorer import python_venv
from sphinx_explorer.util.commander import commander
from ..task import push_task
from .. import package_mgr
from ..package_mgr import SphinxPackageModel


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
        self._selection_model = None

        self.package_tree_view = QTreeView(self)
        self.package_tree_view.setRootIsDecorated(False)
        self.package_tree_view.setSelectionMode(QAbstractItemView.ExtendedSelection)

        self.install_button = QPushButton(self)
        self.update_button = QPushButton(self)

        self.install_button.setText(self.tr("Install"))
        self.update_button.setText(self.tr("Update"))

        self.button_layout = QHBoxLayout()
        self.button_layout.setAlignment(Qt.AlignLeft)
        self.button_layout.addWidget(self.install_button)
        self.button_layout.addWidget(self.update_button)

        self.v_layout = QVBoxLayout(self)
        self.layout = QFormLayout()
        self.v_layout.addLayout(self.layout)
        self.v_layout.addWidget(self.package_tree_view)
        self.v_layout.addLayout(self.button_layout)

        self.setLayout(self.v_layout)

        self.control_dict = {}
        self.python_combo = None

        self.loading_label = LoadingLabel(self.package_tree_view)
        self.loading_label.hide()

        self._connect()

    # noinspection PyUnresolvedReferences
    def _connect(self):
        self.install_button.clicked.connect(self._install)
        self.update_button.clicked.connect(self._update)

    def setup(self, property_model, root_index):
        # type: (PropertyModel, QModelIndex) -> None
        self.property_model = property_model
        self.root_index = root_index

        for item in property_model.properties(root_index):
            control = item.value_type.control(None, item, self)
            control.set_value(item.value)
            self.control_dict[item.key] = control
            self.layout.addRow(item.text(), control)

        combo = self.control_dict["python"]
        combo.combo_box.currentIndexChanged.connect(self._on_interpreter_changed)
        self.python_combo = combo

        self._on_interpreter_changed(combo.currentIndex())

    def _start_loading(self):
        self.loading_label.show()
        self.install_button.setEnabled(False)
        self.update_button.setEnabled(False)

    def _end_loading(self):
        self.loading_label.hide()
        self.install_button.setEnabled(False)
        self.update_button.setEnabled(False)
        self.package_tree_view.resizeColumnToContents(0)

    def _commander(self):
        venv_setting = self.python_combo.value()
        activate_command = python_venv.activate_command(venv_setting)
        return commander.create_pre_commander(activate_command)

    def _install(self):
        install_list, _ = self._item_filter(
            self.package_tree_view.model(),
            self.package_tree_view.selectedIndexes()
        )
        if install_list:
            for package_item in install_list:
                model = package_item.model()    # type: SphinxPackageModel
                if model:
                    model.install(package_item)

    def _update(self):
        _, update_list = self._item_filter(
            self.package_tree_view.model(),
            self.package_tree_view.selectedIndexes()
        )
        if update_list:
            packages = [x.package for x in update_list]

            self._start_loading()
            task = PipInstallTask(packages, update_flag=True)
            task.finished.connect(self._on_install_finished)
            push_task(task)

    def _on_install_finished(self, _):
        self._end_loading()

    def _on_loading_state_changed(self, was_loaded):
        if was_loaded:
            self._end_loading()
        else:
            self._start_loading()

    def _setup_model(self, model):
        if self._selection_model:
            self._selection_model.selectionChanged.disconnect(self._on_selection_changed)

        self.package_tree_view.setModel(model)

        model.loadingStateChanged.connect(self._on_loading_state_changed)
        self._on_loading_state_changed(model.was_loaded)

        self._selection_model = self.package_tree_view.selectionModel()
        self._selection_model.selectionChanged.connect(self._on_selection_changed)

    def _on_selection_changed(self, selected, _):
        if not self._selection_model:
            return

        model = self._selection_model.model()
        install_list, update_list = self._item_filter(model, selected.indexes())

        self.install_button.setEnabled(bool(install_list))
        self.update_button.setEnabled(bool(update_list))

    @staticmethod
    def _item_filter(model, indexes):
        install_list = []
        update_list = []

        for index in indexes:
            if index.column() != 0:
                continue

            item = model.itemFromIndex(index)
            if item:
                if item.version is None:
                    install_list.append(item)
                elif item.latest is not None:
                    update_list.append(item)

        return install_list, update_list

    @Slot(int)
    def _on_interpreter_changed(self, _):
        item = self.property_model.get("python", self.root_index)
        item.value_item.set_value(self.python_combo.value())

        venv_setting = self.python_combo.value()

        model = package_mgr.get_model(venv_setting.python_env())
        self._setup_model(model)

    def teardown(self):
        pass
