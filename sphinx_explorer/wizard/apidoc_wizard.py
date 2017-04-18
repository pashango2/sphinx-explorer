#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division, print_function, absolute_import, unicode_literals

from PySide.QtCore import *
from PySide.QtGui import *

from sphinx_explorer.generator import apidoc
from .base_wizard import BaseWizard, PropertyPage, ExecCommandPage

WIZARD_TOML = "apidoc.toml"


class ApidocWizard(BaseWizard):
    def path(self):
        return self._value_dict.get("path")


class ApiDocSecondPropertyPage(PropertyPage):
    # def initializePage(self):
    #     super(ApiDocSecondPropertyPage, self).initializePage()
    #
    #     root_path = self.wizard().value("path")
    #     item = self.property_widget.item("apidoc-sourcedir")
    #     item.set_link_value(root_path)
    #
    #     self.property_widget.update_default()
    pass


class ApiDocExecCommandPage(ExecCommandPage):
    def initializePage(self):
        super(ApiDocExecCommandPage, self).initializePage()
        model = self.property_model.create_table_model(QModelIndex(), self)
        self.property_widget.setModel(model)

    def exec_(self):
        super(ApiDocExecCommandPage, self).exec_()

        settings = self.dump()
        cmd = apidoc.create_command(
            settings["path"],
            settings["apidoc-sourcedir"],
            settings,
        )
        self.exec_command(cmd)

    def finished(self, return_code):
        super(ApiDocExecCommandPage, self).finished(return_code)
        params = self.dump()
        apidoc.fix_apidoc(
            params["path"],
            params["apidoc-sourcedir"],
            params,
            self.wizard().default_values,
        )


def create_wizard(params_dict, default_settings, parent=None):
    wizard = ApidocWizard(params_dict, default_settings, parent)

    # for Windows
    # For default VistaStyle painting hardcoded in source of QWizard(qwizard.cpp[1805]).
    wizard.setWizardStyle(QWizard.ClassicStyle)

    # last page is disable back button.
    wizard.setOption(QWizard.DisabledBackButtonOnLastPage, True)

    property_model = wizard.property_model

    property_model.load_settings(
        [
            "#*Path setting",
            [
                "*project",
                "path",
            ],
            "#*Project setting",
            [
                "*apidoc-sourcedir",
                "author",
                "html_theme",
                "apidoc-separate",
                "apidoc-private",
            ]
        ],
        params_dict,
        default_values=default_settings,
    )

    first_page = PropertyPage(
        "Path setting",
        property_model,
        property_model.get("Path setting").index(),
        parent=wizard,
    )

    sec_page = ApiDocSecondPropertyPage(
        "Project setting",
        property_model,
        property_model.get("Project setting").index(),
        parent=wizard,
    )

    wizard.addPage(first_page)
    wizard.addPage(sec_page)
    wizard.addPage(
        ApiDocExecCommandPage(
            "create api doc",
            property_model,
            parent=wizard
        )
    )

    wizard.setWindowTitle("Sphinx Apidoc Wizard")
    wizard.resize(QSize(1000, 600).expandedTo(wizard.minimumSizeHint()))

    # disable default button
    wizard.setOption(QWizard.NoDefaultButton, True)

    # noinspection PyUnresolvedReferences
    return wizard


