#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division, print_function, absolute_import, unicode_literals
# from PySide.QtCore import *
from PySide.QtGui import *
from six import string_types

from sphinx_explorer import property_widget


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
        # item_params = {}
        # for item in items:
        #     if isinstance(item, string_types):
        #         if item[0] == "#":
        #             label, item_key = item[1:], None
        #         else:
        #             param = params_dict.get(item)
        #             if param is None:
        #                 raise ValueError(item)
        #             label, item_key = param["label"], item
        #
        #     elif isinstance(item, list):
        #         label, item_key = item
        #     else:
        #         raise
        #
        #     if item_key is None:
        #         self.property_widget.add_category(label)
        #         continue
        #
        #     if isinstance(item_key, dict):
        #         key = item_key["key"]
        #         param = params_dict.get(key).copy()
        #         param.update(item_key)
        #         item_key = key
        #     else:
        #         param = params_dict.get(item_key)
        #
        #     self.property_widget.add_property(
        #         item_key,
        #         param,
        #         label,
        #     )
        #     item_params[item_key] = param

        self.property_widget.resizeColumnsToContents()
        self.property_widget.itemChanged.connect(self._onItemChanged)

        self.setTitle(title)

    # def validatePage(self):
    #     print("validatePage")
    #     return False

    def _onCurrentChanged(self, current, _):
        html = self.property_widget.html(current)
        if html:
            self.text_browser.setHtml(html)
        else:
            self.text_browser.clear()

    def isComplete(self):
        return self.property_widget.is_complete()

    def _onItemChanged(self, _):
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
    def __init__(self, parent=None):
        super(BaseWizard, self).__init__(parent)
        self._value_dict = {}

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

        # self.setOption(QWizard.HaveCustomButton1, True)
        # self.setButtonText(QWizard.CustomButton1, "Create")
        # self.setButtonLayout([
        #     QWizard.Stretch, QWizard.BackButton, QWizard.NextButton,
        #     QWizard.CustomButton1, QWizard.FinishButton, QWizard.CancelButton
        # ])

    def set_value(self, key, value):
        self._value_dict[key] = value

    def value(self, key):
        return self._value_dict[key]
