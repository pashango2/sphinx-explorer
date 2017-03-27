#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division, print_function, absolute_import, unicode_literals
from . import quickstart

from PySide.QtCore import *
from PySide.QtGui import *

from .property_widget import PropertyWidget
from .quickstart import QuickStartDialog


class PropertyWizard(QWizardPage):
    def __init__(self, category_name, params, parent=None):
        # type: (str, dict, QWidget or None) -> None
        super(PropertyWizard, self).__init__(parent)

        self.setTitle(category_name)

        property_widget = PropertyWidget(self)
        for param_key, value_dict in params.items():
            item = property_widget.add_property(
                param_key,
                value_dict.get("name"),
                value_dict.get("default"),
                value_dict.get("description"),
                QuickStartDialog.find_value_type(value_dict.get("value_type")),
            )

            if value_dict.get("description"):
                item.setToolTip(value_dict.get("description").strip())

        layout = QVBoxLayout(self)

        text_browser = QTextBrowser(self)
        splitter = QSplitter(self)
        splitter.addWidget(property_widget)
        splitter.addWidget(text_browser)
        splitter.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        layout.addWidget(splitter)
        self.setLayout(layout)

        def _onCurrentChanged(current, _):
            html = property_widget.html(current)
            if html:
                text_browser.setHtml(html)
            else:
                text_browser.clear()

        property_widget.currentChanged.connect(_onCurrentChanged)
        property_widget.setCurrentIndex(property_widget.index(0, 1))

        self.property_widget = property_widget
        text_browser.setFocusPolicy(Qt.NoFocus)

        self.setTabOrder(self.property_widget, None)

        self.property_widget.resizeColumnToContents(0)

    def initializePage(self):
        self.property_widget.setFocus()


def main(parent):
    settings = quickstart.quickstart_settings()

    wizard = QWizard(parent)
    for category_name, params in settings.items():
        wizard.addPage(PropertyWizard(category_name, params))

    wizard.setWindowTitle("Sphinx Quckstart Wizard")
    wizard.resize(QSize(1000, 600).expandedTo(wizard.minimumSizeHint()))

    # disable default button
    wizard.setOption(QWizard.NoDefaultButton, True)

    # noinspection PyUnresolvedReferences
    wizard.show()
