#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division, print_function, absolute_import, unicode_literals

from PySide.QtCore import *
from PySide.QtGui import *

from sphinx_explorer.property_widget import PropertyWidget
from sphinx_explorer.quickstart import QuickStartWidget
from .base_wizard import PropertyPage, BaseWizard, ExecCommandPage
from sphinx_explorer import quickstart


class ChoiceTemplatePage(QWizardPage):
    def __init__(self, parent=None):
        super(ChoiceTemplatePage, self).__init__(parent)
        self.tree_view_template = QTreeView(self)
        self.text_browser = QTextBrowser(self)
        self.splitter = QSplitter(self)

        self.splitter.addWidget(self.tree_view_template)
        self.splitter.addWidget(self.text_browser)
        self.splitter.setSizePolicy(
            QSizePolicy.Expanding, QSizePolicy.Expanding
        )

        layout = QVBoxLayout(self)
        layout.addWidget(self.splitter)
        self.setLayout(layout)

        self.setTitle("Choice template")


class QuickstartExecCommandPage(ExecCommandPage):
    def initializePage(self):
        self.validatePage()
        self.console_widget.clear()

        settings = self.wizard().dump()
        cmd = quickstart.quickstart_cmd(settings)
        self.exec_command(cmd)

    def finished(self, return_code):
        super(QuickstartExecCommandPage, self).finished(return_code)
        if return_code == 0:
            settings = self.wizard().dump()
            quickstart.fix(settings)


class QuickStartWizard(BaseWizard):
    def path(self):
        return self._value_dict.get("path")


Questions = [
    [
        "Required params",
        [
            "project",
            "path",
            "author",
            "version",
            "release",
        ]
    ],
    [
        "Document params",
        [
            "language",
            "html_theme",
            "epub",
        ]
    ],
    [
        "Options",
        [
            "sep",
            "prefix",
            "suffix",
            "master",
            "#Build params",
            "makefile",
            "batchfile",
            '#Extensions',
            "ext-autodoc",
            "ext-doctest",
            "ext-intersphinx",
            "ext-todo",
            "ext-coverage",
            "ext-imgmath",
            "ext-mathjax",
            "ext-ifconfig",
            "ext-viewcode",
            "ext-githubpage",
        ]
    ],
    [
        "More Extensions",
        [
            "ext-commonmark",
            "ext-nbsphinx",
            "ext-fontawesome",
            "ext-blockdiag",
            "ext-autosummary",
        ]
    ],
]


def create_wizard(params_dict, default_settings, parent=None):
    wizard = QuickStartWizard(parent)

    # for Windows
    # For default VistaStyle painting hardcoded in source of QWizard(qwizard.cpp[1805]).
    wizard.setWizardStyle(QWizard.ClassicStyle)

    params_dict["path"]["require_input"] = False

    wizard.addPage(ChoiceTemplatePage(wizard))

    for category_name, params in Questions:
        wizard.addPage(
            PropertyPage(
                params_dict,
                category_name,
                params,
                default_settings
            )
        )

    wizard.addPage(QuickstartExecCommandPage("finish", wizard))

    params_dict["path"]["require_input"] = True

    # wizard.addPage(FinishWizard(questions))
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
