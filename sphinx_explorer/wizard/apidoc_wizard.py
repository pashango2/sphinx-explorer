#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division, print_function, absolute_import, unicode_literals
import os
from PySide.QtCore import *
from PySide.QtGui import *

from sphinx_explorer.quickstart import QuickStartWidget
from .base_wizard import BaseWizard, PropertyPage, ExecCommandPage
from .. import apidoc

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


class ApidocWizard(BaseWizard):
    # def accept(self):
    #     self.validateCurrentPage()
    #
    #     settings = self.dump()
    #     result = apidoc.create(
    #         settings["path"],
    #         settings["apidoc-sourcedir"],
    #         settings,
    #         cwd=settings["path"],
    #     )
    #     if result == 0:
    #         super(ApidocWizard, self).accept()
    def path(self):
        return self._value_dict.get("path")


class FirstPage(PropertyPage):
    pass


class SecondPropertyPage(PropertyPage):
    def initializePage(self):
        super(SecondPropertyPage, self).initializePage()

        self.property_widget.set_default_value(
            "project",
            os.path.basename(self.wizard().value("apidoc-sourcedir"))
        )
        self.property_widget.update_default()


class ApiDocExecCommandPage(ExecCommandPage):
    def initializePage(self):
        self.validatePage()
        self.console_widget.clear()

        settings = self.wizard().dump()
        cmd = apidoc.create_command(
            settings["path"],
            settings["apidoc-sourcedir"],
            settings,
        )
        self.exec_command(cmd, cwd=settings["path"])


def create_wizard(params_dict, default_settings, parent=None):
    wizard = ApidocWizard(parent)

    # for Windows
    # For default VistaStyle painting hardcoded in source of QWizard(qwizard.cpp[1805]).
    wizard.setWizardStyle(QWizard.ClassicStyle)

    # last page is disable back button.
    wizard.setOption(QWizard.DisabledBackButtonOnLastPage, True)

    page = FirstPage(
        params_dict,
        "First setting",
        [
            "path",
            "apidoc-sourcedir",
            "html_theme",
            "apidoc-separate",
            "apidoc-private",
        ],
        default_settings,
        parent=wizard,
    )
    wizard.addPage(page)

    page = SecondPropertyPage(
        params_dict,
        "Second setting",
        [
            "project",
            "author",
        ],
        default_settings,
        parent=wizard,
    )
    wizard.addPage(page)

    wizard.addPage(ApiDocExecCommandPage("create api doc", parent=wizard))

    # wizard.setup(
    #     wizard_settings.get("wizard", {}),
    #     wizard_settings.get("params", {}),
    #     default_dict=default_settings,
    # )

    wizard.setWindowTitle("Sphinx Apidoc Wizard")
    wizard.resize(QSize(1000, 600).expandedTo(wizard.minimumSizeHint()))

    # disable default button
    wizard.setOption(QWizard.NoDefaultButton, True)

    # noinspection PyUnresolvedReferences
    return wizard


