#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division, print_function, absolute_import, unicode_literals
from PySide.QtCore import *
from PySide.QtGui import *

from sphinx_explorer.property_widget import PropertyWidget
from sphinx_explorer.quickstart import QuickStartWidget

try:
    from . import BaseWizard
except ValueError:
    from __init__ import BaseWizard

WIZARD_TOML = "apidoc.toml"


class FinishWizard(QWizardPage):
    def __init__(self, questions, parent=None):
        # type: (dict, QWidget) -> None
        super(FinishWizard, self).__init__(parent)
        self.questions = questions

        self.widget = QuickStartWidget(parent)
        self.finished = False
        self.widget.finished.connect(self.onFinished)

        self.setTitle("Finish")
        self.property_widget = self.widget.ui.property_widget

        layout = QVBoxLayout(self)
        layout.addWidget(self.widget)
        self.setLayout(layout)

    def initializePage(self):
        wizard = self.wizard()
        default_values = wizard.settings()

        self.property_widget.load_settings(self.questions.keys())
        self.property_widget.load(default_values)
        self.property_widget.resizeColumnToContents(0)

        self.wizard().validateCurrentPage()

    # noinspection PyMethodMayBeStatic
    def dump(self):
        return {}

    def onFinished(self, success, path):
        self.finished = success
        self.wizard().validateCurrentPage()

        if success:
            self.wizard().finished_callback(path)

    def validatePage(self):
        return self.finished


class PropertyWizard(QWizardPage):
    def __init__(self, category_name, params, default_settings, parent=None):
        # type: (str, dict, dict, QWidget or None) -> None
        super(PropertyWizard, self).__init__(parent)

        self.setTitle(category_name)

        property_widget = PropertyWidget(self)
        property_widget.load_settings(params, default_settings)

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


class ApidocWizard(BaseWizard):
    def accept(self):
        return


def create_wizard(wizard_settings, default_settings, parent=None):
    wizard = ApidocWizard(parent)

    # for Windows
    # For default VistaStyle painting hardcoded in source of QWizard(qwizard.cpp[1805]).
    wizard.setWizardStyle(QWizard.ClassicStyle)

    wizard.setup(
        wizard_settings.get("wizard", {}),
        wizard_settings.get("params", {}),
        default_dict=default_settings,
    )

    wizard.setWindowTitle("Sphinx Apidoc Wizard")
    wizard.resize(QSize(1000, 600).expandedTo(wizard.minimumSizeHint()))

    # disable default button
    wizard.setOption(QWizard.NoDefaultButton, True)

    # noinspection PyUnresolvedReferences
    return wizard


def main():
    import os
    import toml
    import sys

    app = QApplication(sys.argv)

    setting_path = os.path.abspath(os.path.join("..", "..", "settings", "apidoc.toml"))
    wizard_settings = toml.load(setting_path)
    print(wizard_settings)

    wizard = create_wizard(wizard_settings, {}, None)
    wizard.exec_()

    app.exec_()


if __name__ == "__main__":
    main()
