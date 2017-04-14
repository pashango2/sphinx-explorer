#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division, print_function, absolute_import, unicode_literals
from PySide.QtGui import *
from PySide.QtCore import *
import os
import yaml
from six import string_types

if False:
    from typing import Optional


class TemplateModel(QStandardItemModel):
    sphinxInfoLoaded = Signal(QModelIndex)
    autoBuildRequested = Signal(str, QStandardItem)

    def __init__(self, parent=None):
        super(TemplateModel, self).__init__(parent)
        self.setHorizontalHeaderLabels([
            self.tr("Template")
        ])

    def load_plugin(self, yaml_path):
        # type: (string_types) -> None
        template_obj = yaml.load(open(yaml_path))
        root_path = os.path.dirname(yaml_path)
        item = TemplateItem(template_obj["title"], template_obj, root_path)
        self.appendRow(item)

    def find(self, title):
        # type: (string_types) -> Optional[TemplateItem]
        items = self.findItems(title)
        if items:
            return items[0]
        return None


class TemplateItem(QStandardItem):
    def __init__(self, name, template, root_path):
        super(TemplateItem, self).__init__(name)
        self.template = template
        self.root_path = root_path

    @property
    def default_values(self):
        return self.template.get("default_values")

    @property
    def description(self):
        return self.template.get("description")

    def wizard_iter(self):
        odd = 0
        category = None
        for x in self.template.get("wizard", []):
            if odd == 0:
                category = x
                odd = 1
            else:
                yield category, x
                odd = 0




