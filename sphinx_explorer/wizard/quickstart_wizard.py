#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division, print_function, absolute_import, unicode_literals
from PySide.QtCore import *
from PySide.QtGui import *

from sphinx_explorer import quickstart
from .base_wizard import PropertyPage, BaseWizard, ExecCommandPage


class ChoiceTemplatePage(QWizardPage):
    def __init__(self, template_model, parent=None):
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
        self.tree_view_template.setModel(template_model)
        self.tree_view_template.setEditTriggers(QAbstractItemView.NoEditTriggers)

    def initializePage(self):
        self.setFinalPage(False)

    def choice(self):
        # type() -> TemplateItem
        index = self.tree_view_template.currentIndex()
        return self.tree_view_template.model().itemFromIndex(index)


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

    def nextId(self):
        return -1


class QuickStartWizard(BaseWizard):
    def __init__(self, params_dict, default_settings, parent=None):
        super(QuickStartWizard, self).__init__(parent)
        self.params_dict = params_dict
        self.default_settings = default_settings
        self.page_dict = {}

    def path(self):
        return self._value_dict.get("path")

    def create_final_page(self):
        page = QuickstartExecCommandPage("finish", self)
        page.setFinalPage(True)
        return page

    def create_template_page(self, template_item):
        if id(template_item) in self.page_dict:
            return self.page_dict[id(template_item)]

        page_ids = []
        last_page = None
        for category_name, params in template_item.wizard_iter():
            last_page = PropertyPage(
                self.params_dict,
                category_name,
                params,
                self.default_settings
            )
            page_id = self.addPage(last_page)
            page_ids.append(page_id)

        if last_page:
            last_page.next_id = 1
            return page_ids[0]
        return -1

    def nextId(self):
        current_id = self.currentId()
        if current_id == 0:
            template_item = self.currentPage().choice()
            if template_item:
                return self.create_template_page(template_item)

        return super(QuickStartWizard, self).nextId()


def create_wizard(template_model, params_dict, default_settings, parent=None):
    wizard = QuickStartWizard(params_dict, default_settings, parent)

    # for Windows
    # For default VistaStyle painting hardcoded in source of QWizard(qwizard.cpp[1805]).
    wizard.setWizardStyle(QWizard.ClassicStyle)

    wizard.addPage(ChoiceTemplatePage(template_model, wizard))
    wizard.addPage(wizard.create_final_page())

    wizard.setWindowTitle("Sphinx Apidoc Wizard")
    wizard.resize(QSize(1000, 600).expandedTo(wizard.minimumSizeHint()))

    # disable default button
    wizard.setOption(QWizard.NoDefaultButton, True)

    # noinspection PyUnresolvedReferences
    return wizard
