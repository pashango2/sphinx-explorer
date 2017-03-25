#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division, print_function, absolute_import, unicode_literals
from . import quickstart

from PySide.QtCore import *
from PySide.QtGui import *

from .property_widget import PropertyWidget
from .quickstart import QuickStartDialog


def create_intro_page(category_name, params):
    # type: (str, dict) -> QWizardPage
    page = QWizardPage()
    page.setTitle(category_name)

    property_widget = PropertyWidget(page)
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

    layout = QVBoxLayout(page)

    text_browser = QTextBrowser(page)
    splitter = QSplitter(page)
    splitter.addWidget(property_widget)
    splitter.addWidget(text_browser)
    splitter.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

    layout.addWidget(splitter)
    page.setLayout(layout)

    def _onCurrentChanged(current, _):
        html = property_widget.html(current)
        if html:
            text_browser.setHtml(html)
        else:
            text_browser.clear()

    property_widget.currentChanged.connect(_onCurrentChanged)
    property_widget.setCurrentIndex(property_widget.index(0, 1))

    property_widget.setFocus()

    return page


def main(parent):
    settings = quickstart.quickstart_settings()

    wizard = QWizard(parent)
    for category_name, params in settings.items():
        wizard.addPage(create_intro_page(category_name, params))

    wizard.setWindowTitle("Sphinx Quckstart Wizard")
    wizard.resize(QSize(1000, 600).expandedTo(wizard.minimumSizeHint()))

    # disable default button
    wizard.setOption(QWizard.NoDefaultButton, True)

    # noinspection PyUnresolvedReferences
    wizard.show()
