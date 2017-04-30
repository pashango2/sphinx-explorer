#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division, print_function, absolute_import, unicode_literals
from qtpy.QtCore import *
# from qtpy.QtGui import *
from qtpy.QtWidgets import *
from six import string_types
from sphinx_explorer.util.QConsoleWidget import QConsoleWidget
from sphinx_explorer.util import icon

from sphinx_explorer import property_widget
from sphinx_explorer.property_widget import PropertyModel, DescriptionWidget, DefaultValues


# noinspection PyArgumentList
class ExecCommandPage(QWizardPage):
    BUTTON_HEIGHT = 64
    BUTTON_ICON_SIZE = 28

    # noinspection PyTypeChecker
    def __init__(self, title, property_model, parent=None):
        # type: (string_types, QWidget) -> None
        super(ExecCommandPage, self).__init__(parent)
        self.console_widget = QConsoleWidget(self)
        self.property_model = property_model
        self.property_widget = property_widget.PropertyWidget(self, property_model)
        self.gen_button = QPushButton(self)
        self.gen_button.setMinimumHeight(self.BUTTON_HEIGHT)
        self.gen_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.gen_button.setIconSize(QSize(self.BUTTON_ICON_SIZE, self.BUTTON_ICON_SIZE))

        self.v_layout = QVBoxLayout(self)
        self.v_layout.addWidget(self.gen_button)
        self.v_layout.addWidget(self.console_widget)
        self.v_layout.setContentsMargins(0, 0, 0, 0)
        self.panel = QWidget(self)
        self.panel.setLayout(self.v_layout)
        self.panel.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.splitter = QSplitter(self)
        self.splitter.addWidget(self.property_widget)
        self.splitter.addWidget(self.panel)
        self.splitter.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.splitter.setStretchFactor(1, 1)
        self.splitter.setSizes([310, 643])

        layout = QVBoxLayout(self)
        layout.addWidget(self.splitter)
        self.setLayout(layout)

        self.console_widget.finished.connect(self.finished)
        # noinspection PyUnresolvedReferences
        self.gen_button.clicked.connect(self.exec_)

        self.setTitle(title)
        self.gen_button.setText(self.tr(str("Generate")))
        self.gen_button.setIcon(icon.load("thunder"))

        self.setTabOrder(self.gen_button, self.console_widget)
        self.setTabOrder(self.console_widget, self.property_widget)
        self.succeeded = False
        self.cmd = ""

    def initializePage(self):
        self.validatePage()

        # settings, params_dict = self.wizard().all_props()
        # self.property_widget.load_settings(settings, params_dict)
        self.property_widget.setup()
        # self.property_widget.set_values(self.wizard().dump())

        self.property_widget.resizeColumnsToContents()
        self.gen_button.setFocus()

    def isComplete(self):
        return self.succeeded

    def validatePage(self):
        return self.succeeded

    def exec_(self):
        self.console_widget.clear()

    def exec_command(self, cmd, cwd=None):
        self.cmd = cmd
        self.console_widget.exec_command(cmd, cwd)

    def dump(self):
        # type: () -> dict
        wizard = self.wizard()  # type: BaseWizard
        d = wizard.default_values.copy()
        d.update(self.property_widget.dump(flat=True))
        return d

    def finished(self, return_code):
        self.succeeded = return_code == 0
        # noinspection PyUnresolvedReferences
        self.completeChanged.emit()
        self.validatePage()

        if self.succeeded is False:
            # noinspection PyCallByClass
            QMessageBox.critical(self, "Error", "Error")
            self.wizard().button(QWizard.BackButton).setEnabled(True)
        else:
            self.gen_button.setEnabled(False)

            path = self.dump().get("path")
            if path:
                self.wizard().addDocumentRequested.emit(path)


# noinspection PyArgumentList
class PropertyPage(QWizardPage):
    def __init__(self, title, model, root_index, vbox_flag=False, parent=None):
        super(PropertyPage, self).__init__(parent)
        self.model = model

        self.property_widget = property_widget.PropertyWidget(self, self.model)
        self.property_widget.setRootIndex(root_index)
        self.property_widget.setup()

        layout = QVBoxLayout(self)

        if vbox_flag is False:
            self.text_browser = DescriptionWidget(self)
            self.splitter = QSplitter(self)

            self.splitter.addWidget(self.property_widget)
            self.splitter.addWidget(self.text_browser)
            self.splitter.setSizePolicy(
                QSizePolicy.Expanding, QSizePolicy.Expanding
            )
            self.splitter.setStretchFactor(1, 1)
            self.splitter.setSizes([310, 643])

            layout.addWidget(self.splitter)
        else:
            self.text_browser = None
            layout.addWidget(self.property_widget)

        self.setLayout(layout)

        self.selection_model = self.property_widget.selectionModel()
        # noinspection PyUnresolvedReferences
        self.selection_model.currentChanged.connect(self._onCurrentChanged)
        self.property_widget.setCurrentIndex(self.property_widget.index(0, 1))

        self.property_widget.resizeColumnsToContents()
        self.property_widget.model().itemChanged.connect(self._onItemChanged)

        self.setTitle(title)

        self.next_id = -1

    def nextId(self):
        if self.next_id > 0:
            return self.next_id
        return super(PropertyPage, self).nextId()

    @Slot(QModelIndex, QModelIndex)
    def _onCurrentChanged(self, current, _):
        if self.text_browser is None:
            return

        title = self.property_widget.title(current)
        description, search_path = self.property_widget.description(current)

        self.text_browser.setMarkdown(description or "", title=title, search_path=search_path)
        # if description:
        #     self.text_browser.setMarkdown(description, title=title)
        # else:
        #     self.text_browser.clear()

    def isComplete(self):
        return self.property_widget.is_complete()

    def _onItemChanged(self, _):
        # noinspection PyUnresolvedReferences
        self.completeChanged.emit()

    def initializePage(self):
        # type: () -> None
        self.property_widget.setFocus()
        index = self.property_widget.first_property_index()
        self.property_widget.setCurrentIndex(index)
        self.property_widget.update_link()
        self.property_widget.resizeColumnsToContents()

    def validatePage(self):
        prop_obj = self.property_widget.dump()
        for key, value in prop_obj.items():
            self.wizard().set_value(key, value)

        return True

    def keys(self):
        return self.property_widget.dump().keys()


# noinspection PyArgumentList
class BaseWizard(QWizard):
    addDocumentRequested = Signal(str)

    def __init__(self, params_dict, default_values, parent=None):
        super(BaseWizard, self).__init__(parent)
        self._value_dict = {}
        self.params_dict = params_dict
        _default_values = {}
        for key, value in params_dict.items():
            if "default" in value:
                _default_values[key] = value.get("default")
        _default_values.update(default_values)
        self.default_values = DefaultValues(_default_values)
        self.property_model = PropertyModel(self)

    def setup(self, setting_dict, params_dict, default_dict=None):
        # type: (dict) -> None
        order = setting_dict.get('_order', setting_dict.keys())

        for page_name in order:
            page_data = setting_dict[page_name]

            # noinspection PyTypeChecker
            page = PropertyPage(
                params_dict,
                page_data.get("params", []),
                default_dict,
                self
            )
            page.setTitle(page_name)
            self.addPage(page)

    def set_value(self, key, value):
        self._value_dict[key] = value

    def value(self, key):
        return self._value_dict[key]

    def dump(self):
        d = self.default_values.copy()
        d.update(self._value_dict)
        return d

    def all_props(self):
        props = []
        for page_id in self.visitedPages():
            page = self.page(page_id)
            if isinstance(page, PropertyPage):
                props.append("# " + page.title())
                props += page.keys()

        return props, self.params_dict
