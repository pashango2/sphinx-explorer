#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division, print_function, absolute_import, unicode_literals
from qtpy.QtWidgets import *
from . import Page
from ..property_view import PropertyView
from ..py_config import ConfigModel


class WizardPages(Page):
    def __init__(self, config_model, parent=None):
        super(WizardPages, self).__init__(parent)
        self.config_model = config_model
        self.parent = parent
        self._controls = []

    def setup(self):
        config_model = self.config_model    # type: ConfigModel
        parent = self.parent
        pages = []

        for header_item in config_model.headers():
            page = QWizardPage(parent)
            page.setTitle(header_item.text())

            view = PropertyView(page)
            view.setModel(config_model, header_item.index())

            layout = QVBoxLayout()
            layout.addWidget(view)

            page.setLayout(layout)

            pages.append(page)

        return pages

    def commit(self):
        pass
