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


class ApiDOcSecondPropertyPage(PropertyPage):
    def initializePage(self):
        super(ApiDOcSecondPropertyPage, self).initializePage()

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

    def finished(self, returncode, _):
        super(ApiDocExecCommandPage, self).finished(returncode, _)

        settings = self.wizard().dump()
        apidoc.create_setting_toml(
            settings["path"],
            settings["apidoc-sourcedir"],
        )


def create_wizard(params_dict, default_settings, parent=None):
    wizard = ApidocWizard(parent)

    # for Windows
    # For default VistaStyle painting hardcoded in source of QWizard(qwizard.cpp[1805]).
    wizard.setWizardStyle(QWizard.ClassicStyle)

    # last page is disable back button.
    wizard.setOption(QWizard.DisabledBackButtonOnLastPage, True)

    first_page = PropertyPage(
        params_dict,
        "Path setting",
        [
            "path",
            "apidoc-sourcedir",
        ],
        default_settings,
        parent=wizard,
    )

    sec_page = ApiDOcSecondPropertyPage(
        params_dict,
        "Project setting",
        [
            "project",
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


