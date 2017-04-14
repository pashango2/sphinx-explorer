#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division, print_function, absolute_import, unicode_literals
import os
from PySide.QtCore import *
from PySide.QtGui import *

from .base_wizard import BaseWizard, PropertyPage, ExecCommandPage
from .. import apidoc

WIZARD_TOML = "apidoc.toml"


class ApidocWizard(BaseWizard):
    def path(self):
        return self._value_dict.get("path")


class ApiDocSecondPropertyPage(PropertyPage):
    def initializePage(self):
        super(ApiDocSecondPropertyPage, self).initializePage()

        root_path = self.wizard().value("path")
        item = self.property_widget.item("apidoc-sourcedir")
        item.set_link_value(root_path)

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
        self.exec_command(cmd)

    def finished(self, return_code):
        super(ApiDocExecCommandPage, self).finished(return_code)
        settings = self.wizard().dump()
        apidoc.fix_apidoc(
            settings["path"],
            settings["apidoc-sourcedir"],
            settings,
        )


def create_wizard(params_dict, default_settings, parent=None):
    wizard = ApidocWizard(default_settings, parent)

    # for Windows
    # For default VistaStyle painting hardcoded in source of QWizard(qwizard.cpp[1805]).
    wizard.setWizardStyle(QWizard.ClassicStyle)

    # last page is disable back button.
    wizard.setOption(QWizard.DisabledBackButtonOnLastPage, True)

    first_page = PropertyPage(
        params_dict,
        "Path setting",
        [
            "project",
            "path",

        ],
        default_settings,
        parent=wizard,
    )

    sec_page = ApiDocSecondPropertyPage(
        params_dict,
        "Project setting",
        [
            "apidoc-sourcedir",
            "author",
            "html_theme",
            "apidoc-separate",
            "apidoc-private",
        ],
        default_settings,
        parent=wizard,
    )

    wizard.addPage(first_page)
    wizard.addPage(sec_page)
    wizard.addPage(ApiDocExecCommandPage("create api doc", parent=wizard))

    wizard.setWindowTitle("Sphinx Apidoc Wizard")
    wizard.resize(QSize(1000, 600).expandedTo(wizard.minimumSizeHint()))

    # disable default button
    wizard.setOption(QWizard.NoDefaultButton, True)

    # noinspection PyUnresolvedReferences
    return wizard


