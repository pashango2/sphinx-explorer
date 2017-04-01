#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division, print_function, absolute_import, unicode_literals
from . import quickstart

from PySide.QtCore import *
from PySide.QtGui import *

from .property_widget import PropertyWidget
from .quickstart import get_questions


class PropertyWizard(QWizardPage):
    def __init__(self, category_name, params, default_settings, parent=None):
        # type: (str, dict, dict, QWidget or None) -> None
        super(PropertyWizard, self).__init__(parent)

        print(params)

        self.setTitle(category_name)

        property_widget = PropertyWidget(self)
        property_widget.load_settings(params, default_settings)

        # for item in property_item_iter(property_widget, params):
        #     property_widget.add_property_item(item)

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
        # type: () -> None
        self.property_widget.setFocus()

    def dump(self):
        # type: () -> dict
        return self.property_widget.dump()


class QuickStartWizard(QWizard):
    def accept(self):
        result = dict()

        for page_id in self.visitedPages():
            wiz_page = self.page(page_id)       # type: PropertyWizard
            result.update(wiz_page.dump())

        super(QuickStartWizard, self).accept()


def main(default_settings, parent):
    questions = get_questions()

    wizard = QuickStartWizard(parent)

    # for Windows
    # For default VistaStyle painting hardcoded in source of QWizard(qwizard.cpp[1805]).
    wizard.setWizardStyle(QWizard.ClassicStyle)

    for category_name in questions.categories():
        wizard.addPage(
            PropertyWizard(
                category_name,
                questions.properties(category_name),
                default_settings
            )
        )

    wizard.setWindowTitle("Sphinx Quckstart Wizard")
    wizard.resize(QSize(1000, 600).expandedTo(wizard.minimumSizeHint()))

    # disable default button
    wizard.setOption(QWizard.NoDefaultButton, True)

    # noinspection PyUnresolvedReferences
    wizard.show()

