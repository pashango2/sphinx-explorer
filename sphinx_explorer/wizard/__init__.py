#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division, print_function, absolute_import, unicode_literals
from PySide.QtCore import *
from PySide.QtGui import *
from six import string_types

from sphinx_explorer.property_widget import PropertyWidget
from sphinx_explorer.quickstart import QuickStartWidget

try:
    from .. import property_widget
except ValueError:
    import sys
    sys.path.append("..")
    import property_widget


class PropertyPage(QWizardPage):
    def __init__(self, params_dict, items, default_dict, parent=None):
        super(PropertyPage, self).__init__(parent)

        self.property_widget = property_widget.PropertyWidget(self)
        self.property_widget.set_default_dict(default_dict or {})
        layout = QVBoxLayout(self)
        layout.addWidget(self.property_widget)
        self.setLayout(layout)

        item_params = {}
        for item in items:
            if isinstance(item, string_types):
                if item[0] == "#":
                    label, item_key = item[1:], None
                else:
                    param = params_dict.get(item)
                    label, item_key = param["label"], item

            elif isinstance(item, list):
                label, item_key = item
            else:
                raise

            if item_key is None:
                self.property_widget.add_category(label)
                continue

            if isinstance(item_key, dict):
                key = item_key["key"]
                param = params_dict.get(key).copy()
                param.update(item_key)
                item_key = key
            else:
                param = params_dict.get(item_key)

            self.property_widget.add_property(
                item_key,
                param,
                label,
            )
            item_params[item_key] = param

        self.property_widget.setup_link(item_params)
        self.property_widget.resizeColumnsToContents()

        self.property_widget.itemChanged.connect(self._onItemChanged)

    # def validatePage(self):
    #     print("validatePage")
    #     return False

    def isComplete(self):
        return self.property_widget.is_complete()

    def _onItemChanged(self, _):
        self.completeChanged.emit()

    def initializePage(self):
        # type: () -> None
        print("init")
        self.property_widget.setFocus()
        index = self.property_widget.first_property_index()
        self.property_widget.setCurrentIndex(index)
        self.property_widget.update_link()


class BaseWizard(QWizard):
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


def main():
    import sys

    app = QApplication(sys.argv)

    params_dict = {
        "name": {
            "default": "test",
            "description": """
This is required.
"""
        },
        "checked": {
            "value_type": "TypeBool"
        },
        "path": {
            "value_type": "TypeDirPath"
        },
        "relpath": {
            "value_type": "TypeRelDirPath"
        }
    }

    setting_dict = {
        "first": {
            "params": [
                ["Project params", None],
                ["Project Name", "name"],
                ["checked", "checked"],
                ["path", "path"],
                ["Relate", {
                    "key": "relpath",
                    "path": ".",
                }],
            ],
        },
        # "second": {
        #
        # },

        "_order": [
            "first"
        ],
    }

    default_dicct = {
        "path": "."
    }

    import os
    import toml
    import sys

    setting_path = os.path.abspath(os.path.join("..", "..", "settings", "apidoc.toml"))
    wizard_settings = toml.load(setting_path)

    frame = BaseWizard()
    frame.setWizardStyle(QWizard.ClassicStyle)
    frame.setup(
        wizard_settings.get("wizard", {}),
        wizard_settings.get("params", {}),
    )
    frame.show()

    app.exec_()

if __name__ == "__main__":
    main()
