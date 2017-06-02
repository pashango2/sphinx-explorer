#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division, print_function, absolute_import, unicode_literals
from qtpy.QtWidgets import *
from . import Page


class FormLayoutPage(Page):
    def __init__(self, config_model, parent=None):
        super(FormLayoutPage, self).__init__(parent)
        self.config_model = config_model
        self.parent = parent
        self._controls = []

    def setup(self):
        config_model = self.config_model
        parent = self.parent

        root_layout = QFormLayout()
        layout = root_layout

        for depth, config_item in config_model.config_iter():
            if depth == 0:
                layout = root_layout

            if config_item.is_category:
                if depth == 0:
                    control = QGroupBox(parent)
                    control.setTitle(config_item.text())
                    control.setLayout(QFormLayout(parent))
                    root_layout.addRow(control)

                    layout = control.layout()
                else:
                    layout.addRow(QLabel(config_item.text(), parent))
            else:
                control = config_item.control(parent)
                self._controls.append((config_item, control))
                layout.addRow(config_item.text(), control)

        v_layout = QVBoxLayout()
        v_layout.addLayout(root_layout)
        v_layout.addStretch(0)

        return v_layout

    def commit(self):
        pass
