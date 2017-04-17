#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division, print_function, absolute_import, unicode_literals
from PySide.QtCore import *
from .define import *
from collections import OrderedDict

__all__ = [
    "PropertyFilterModel",
]


class PropertyFilterModel(QSortFilterProxyModel):
    def __init__(self, source_model, property_filter, parent=None):
        super(PropertyFilterModel, self).__init__(parent)
        self.setSourceModel(source_model)
        self.property_filter = property_filter

    def filterAcceptsRow(self, source_row, parent):
        index = self.sourceModel().index(source_row, 0)
        item = self.sourceModel().itemFromIndex(index)

        return item.key in self.property_filter

    def item(self, row):
        index = self.mapToSource(self.index(row, 0))
        return self.sourceModel().itemFromIndex(index)

    def itemFromIndex(self, index):
        index = self.mapToSource(index)
        return self.sourceModel().itemFromIndex(index)

    @property
    def itemChanged(self):
        return self.sourceModel().itemChanged

    def set_default_dict(self, default_dict):
        self.sourceModel().set_default_dict(default_dict)

    def properties(self):
        # type: () -> Iterator[PropertyItem]
        for row in range(self.rowCount()):
            item = self.item(row)
            if item.type() == PropertyItemType:
                yield item

    def rowItem(self, index):
        # type: (QModelIndex) -> PropertyItem
        return self.sourceModel().rowItem(self.mapToSource(index))

    def property_map(self):
        # type: () -> Dict[string_types, PropertyItem]
        prop_map = OrderedDict()
        for item in self.properties():
            prop_map[item.key] = item
        return prop_map