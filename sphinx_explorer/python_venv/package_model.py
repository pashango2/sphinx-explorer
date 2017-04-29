#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division, print_function, absolute_import, unicode_literals

from qtpy.QtGui import *
from sphinx_explorer.python_venv.tasks import *

import logging
logger = logging.getLogger(__name__)

if False:
    from typing import Optional


class PackageModel(QStandardItemModel):
    def __init__(self, parent=None):
        super(PackageModel, self).__init__(parent)
        self._package_dict = {}
        self._is_loaded = False
        self.setHorizontalHeaderLabels([
            self.tr("Package"),
            self.tr("Version"),
            self.tr("Latest"),
        ])
        self.loading = False

    def load(self, packages):
        self.removeRows(0, self.rowCount())
        for package, version, latest in packages:
            self.add_package(package, version, latest)
        self._is_loaded = True

    def clear(self):
        self._package_dict = {}
        self._is_loaded = False
        super(PackageModel, self).clear()

    def find(self, package_name):
        # type: (str) -> Optional[PackageItem]
        # noinspection PyArgumentList
        items = self.findItems(package_name)
        if items:
            return items[0]
        return None

    @staticmethod
    def package_name_filter(name):
        return name.lower().replace(".", "-")

    def add_package(self, package, version, latest, row=-1):
        package = self.package_name_filter(package)

        item = PackageItem(package, version, latest)
        self._package_dict[package] = item

        items = [item, QStandardItem(), QStandardItem()]
        if row < 0:
            self.appendRow(items)
        else:
            self.insertRow(row, items)

    def load_out_date(self, out_date_packages):
        for package, version, latest, _ in out_date_packages:
            if package in self._package_dict:
                item = self._package_dict[package]
                item.latest = latest

    def create_filter_model(self, filter_packages, parent=None):
        filter_packages = [self.package_name_filter(x) for x in filter_packages]

        for package in filter_packages:
            if package not in self._package_dict:
                self.add_package(package, None, 0)

        return PackageFilterModel(self, filter_packages, parent)

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return super(PackageModel, self).data(index, role)

        if index.column() != 0:
            column = index.column()
            index = index.sibling(index.row(), 0)
            if role == Qt.DisplayRole:
                if column == 1:
                    item = self.itemFromIndex(index)    # type: PackageItem
                    return item.version if not item.installing else "Installing..."
                elif column == 2:
                    item = self.itemFromIndex(index)    # type: PackageItem
                    return item.latest or item.version

        return super(PackageModel, self).data(index, role)


class PackageItem(QStandardItem):
    COLOR_OK = QColor("#3b7960")
    COLOR_NOT_INSTALL = QColor("#640125")

    def __init__(self, package, version, latest=None, pack_type=None):
        super(PackageItem, self).__init__(package)
        self.package = package
        self.version = version
        self.latest = latest
        self.pack_type = pack_type
        self.installing = False

        self.update_color()

    def update_color(self):
        if self.version:
            self.setBackground(self.COLOR_OK)
        else:
            self.setBackground(self.COLOR_NOT_INSTALL)


class PackageFilterModel(QSortFilterProxyModel):
    def __init__(self, source_model, package_list, parent=None):
        super(PackageFilterModel, self).__init__(parent)
        self.setSourceModel(source_model)
        self.package_list = package_list

    def filterAcceptsRow(self, source_row, source_parent):
        index = self.sourceModel().index(source_row, 0, source_parent)
        return index.data() in self.package_list
