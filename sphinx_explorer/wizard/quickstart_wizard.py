#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division, print_function, absolute_import, unicode_literals

from qtpy.QtCore import *
# from qtpy.QtGui import *
from qtpy.QtWidgets import *

from sphinx_explorer.generator import quickstart
from .base_wizard import PropertyPage, BaseWizard, ExecCommandPage
from ..property_widget import DescriptionWidget


# noinspection PyArgumentList
class ChoiceTemplatePage(QWizardPage):
    def __init__(self, template_model, parent=None):
        super(ChoiceTemplatePage, self).__init__(parent)
        self.tree_view_template = QTreeView(self)
        self.text_browser = DescriptionWidget(self)
        self.splitter = QSplitter(self)
        # self.splitter.setSizes([])

        self.splitter.addWidget(self.tree_view_template)
        self.splitter.addWidget(self.text_browser)
        self.splitter.setSizePolicy(
            QSizePolicy.Expanding, QSizePolicy.Expanding
        )
        self.splitter.setStretchFactor(1, 1)
        self.splitter.setSizes([310, 643])

        layout = QVBoxLayout(self)
        layout.addWidget(self.splitter)
        self.setLayout(layout)

        self.setTitle(self.tr("Choice template"))
        self.tree_view_template.setModel(template_model)
        self.tree_view_template.setEditTriggers(QAbstractItemView.NoEditTriggers)

        self.template_selection_model = self.tree_view_template.selectionModel()
        # noinspection PyUnresolvedReferences
        self.template_selection_model.currentChanged.connect(self._on_template_current_changed)
        # noinspection PyUnresolvedReferences
        self.tree_view_template.doubleClicked.connect(self._on_double_clicked)
        self.tree_view_template.setCurrentIndex(template_model.index(0, 0))

    def validatePage(self):
        wizard = self.wizard()
        wizard.create_template_page(self.choice())
        wizard.template_item = self.choice()
        return True

    def _on_double_clicked(self, _):
        # type: (QModelIndex) -> None
        self.wizard().next()

    def _on_template_current_changed(self, current, _):
        # type: (QModelIndex, QModelIndex) -> None
        item = self.tree_view_template.model().itemFromIndex(current)

        if item.description:
            self.text_browser.setMarkdown(
                item.description,
                title=item.text(),
                search_path=item.root_path,
            )
        else:
            self.text_browser.clear()

    def choice(self):
        # type() -> TemplateItem
        index = self.tree_view_template.currentIndex()
        return self.tree_view_template.model().itemFromIndex(index)


class QuickstartExecCommandPage(ExecCommandPage):
    def exec_(self):
        super(QuickstartExecCommandPage, self).exec_()

        template_item = self.wizard().template_item
        was_apidoc = template_item.was_apidoc() if template_item else False
        mastertoctree = "   apidoc/modules" if was_apidoc else None

        settings = self.dump()
        quick_start_cmd = quickstart.quickstart_cmd(settings, mastertoctree=mastertoctree)

        if was_apidoc:
            apidoc_cmd = quickstart.apidoc_cmd(settings)
            cmd = [quick_start_cmd, apidoc_cmd]
        else:
            cmd = quick_start_cmd

        self.exec_command(cmd)

    def setModel(self, model):
        self.property_widget.setModel(model)

    def finished(self, return_code):
        if return_code == 0:
            template_item = self.wizard().template_item
            was_apidoc = template_item.was_apidoc() if template_item else False

            params = self.dump()
            quickstart.fix(params, self.wizard().default_values, self.cmd, was_apidoc)

        super(QuickstartExecCommandPage, self).finished(return_code)

    def nextId(self):
        return -1


class QuickStartWizard(BaseWizard):
    START_PAGE = 0
    FINISH_PAGE = 1
    WIZARD_PAGE = 2

    def __init__(self, params_dict, default_settings, parent=None):
        super(QuickStartWizard, self).__init__(params_dict, default_settings, parent)
        self.params_dict = params_dict
        self.page_dict = {}
        self.page_list = []
        self.finish_page = self.create_final_page()
        self.template_item = None

    def setTemplateModel(self, template_model):
        self.setPage(self.START_PAGE, ChoiceTemplatePage(template_model, self))
        self.setPage(self.FINISH_PAGE, self.finish_page)

    def path(self):
        return self._value_dict.get("path")

    def create_final_page(self):
        page = QuickstartExecCommandPage(self.tr("finish"), self.property_model, self)
        page.setFinalPage(True)
        return page

    def create_template_page(self, template_item):
        if id(template_item) in self.page_dict:
            return self.page_dict[id(template_item)]

        self.default_values.pop(1)
        self.default_values.push(template_item.default_values)

        self.property_model.removeRows(0, self.property_model.rowCount())
        self.property_model.load_settings(
            template_item.wizard_settings,
            self.params_dict,
            self.default_values,
        )

        self.page_list = []
        for header_item in self.property_model.headers():
            last_page = PropertyPage(
                header_item.text(),
                self.property_model,
                header_item.index(),
                vbox_flag=header_item.vbox_flag,
            )
            page_id = self.addPage(last_page)
            self.page_list.append(page_id)

        return True

    def nextId(self):
        current_id = self.currentId()
        if self.page_list:
            if current_id == 0:
                return self.page_list[0]
            elif current_id == self.page_list[-1]:
                model = self.property_model.create_table_model(QModelIndex(), self.finish_page)
                self.finish_page.setModel(model)
                return self.FINISH_PAGE

        return super(QuickStartWizard, self).nextId()


def create_wizard(template_model, params_dict, default_settings, parent=None):
    wizard = QuickStartWizard(params_dict, default_settings, parent)
    wizard.setTemplateModel(template_model)

    # for Windows
    # For default VistaStyle painting hardcoded in source of QWizard(qwizard.cpp[1805]).
    wizard.setWizardStyle(QWizard.ClassicStyle)

    wizard.setWindowTitle("Sphinx Apidoc Wizard")
    wizard.resize(QSize(1000, 600).expandedTo(wizard.minimumSizeHint()))

    # disable default button
    wizard.setOption(QWizard.NoDefaultButton, True)

    # noinspection PyUnresolvedReferences
    return wizard
