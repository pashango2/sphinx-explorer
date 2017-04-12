#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division, print_function, absolute_import, unicode_literals
# from PySide.QtCore import *
from PySide.QtGui import *
from six import string_types
from sphinx_explorer.util.QConsoleWidget import QConsoleWidget
from .. import icon

from sphinx_explorer import property_widget


class DefaultValues(object):
    def __init__(self, values_dict):
        self._dicts = [values_dict or {}]

    def __getitem__(self, key):
        for d in self._dicts:
            if key in d:
                return d[key]
        raise KeyError(key)

    def __contains__(self, key):
        for d in self._dicts:
            if key in d:
                return True
        return False

    def items(self):
        for key in self.keys():
            yield key, self[key]

    def get(self, key, default=None):
        for d in self._dicts:
            if key in d:
                return d[key]
        return default

    def push(self, d):
        self._dicts.insert(0, d or {})

    def pop(self, index=0):
        index = len(self._dicts) - 1 - index
        if index < 0:
            return
        try:
            self._dicts.pop(index)
        except IndexError:
            pass

    def keys(self):
        keys = set()
        for d in self._dicts:
            keys |= d.keys()
        return keys

    def copy(self):
        d = {}
        for key, value in self.items():
            d[key] = value
        return d


class ExecCommandPage(QWizardPage):
    def __init__(self, title, parent=None):
        # type: (string_types, QWidget) -> None
        super(ExecCommandPage, self).__init__(parent)
        self.console_widget = QConsoleWidget(self)
        self.console_widget.finished.connect(self.finished)

        layout = QVBoxLayout(self)
        layout.addWidget(self.console_widget)
        self.setLayout(layout)

        self.setTitle(title)
        self.can_finished = False

    def validatePage(self):
        return self.can_finished

    def exec_command(self, cmd, cwd=None):
        self.console_widget.exec_command(cmd, cwd)

    def finished(self, return_code):
        self.can_finished = return_code == 0
        self.validatePage()

        if self.can_finished is False:
            self.wizard().button(QWizard.BackButton).setEnabled(True)


class PropertyPage(QWizardPage):
    def __init__(self, params_dict, title, items, default_dict, parent=None):
        super(PropertyPage, self).__init__(parent)

        self.property_widget = property_widget.PropertyWidget(self)
        self.property_widget.set_default_dict(default_dict or {})
        self.text_browser = QTextBrowser(self)
        self.splitter = QSplitter(self)

        self.splitter.addWidget(self.property_widget)
        self.splitter.addWidget(self.text_browser)
        self.splitter.setSizePolicy(
            QSizePolicy.Expanding, QSizePolicy.Expanding
        )

        layout = QVBoxLayout(self)
        layout.addWidget(self.splitter)
        self.setLayout(layout)

        self.property_widget.currentChanged.connect(self._onCurrentChanged)
        self.property_widget.setCurrentIndex(self.property_widget.index(0, 1))

        self.property_widget.load_settings(
            items,
            params_dict=params_dict,
        )

        self.property_widget.resizeColumnsToContents()
        self.property_widget.itemChanged.connect(self._onItemChanged)

        self.setTitle(title)

        self.next_id = -1

    def nextId(self):
        if self.next_id > 0:
            return self.next_id
        return super(PropertyPage, self).nextId()

    def _onCurrentChanged(self, current, _):
        html = self.property_widget.html(current)
        if html:
            self.text_browser.setHtml(html)
        else:
            self.text_browser.clear()

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

    def validatePage(self):
        prop_obj = self.property_widget.dump()
        for key, value in prop_obj.items():
            self.wizard().set_value(key, value)

        return True


class BaseWizard(QWizard):
    def __init__(self, default_values, parent=None):
        super(BaseWizard, self).__init__(parent)
        self._value_dict = {}
        self.default_values = DefaultValues(default_values)

        self.setOption(QWizard.HaveCustomButton1, True)
        self.setButtonText(QWizard.CustomButton1, self.tr("Add Bookmark"))
        self.setButtonLayout([
            QWizard.CustomButton1, QWizard.Stretch, QWizard.BackButton,
            QWizard.NextButton, QWizard.FinishButton, QWizard.CancelButton
        ])

        button = self.button(QWizard.CustomButton1)
        button.setIcon(icon.load("bookmark"))

    def setup(self, setting_dict, params_dict, default_dict=None):
        # type: (dict) -> None
        order = setting_dict.get('_order', setting_dict.keys())

        for page_name in order:
            page_data = setting_dict[page_name]

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
