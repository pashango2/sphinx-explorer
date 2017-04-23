#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division, print_function, absolute_import, unicode_literals

import fnmatch
import os
from collections import OrderedDict

import six
import toml
import typing
from qtpy.QtCore import *
from qtpy.QtWidgets import *
from qtpy.QtGui import *

from sphinx_explorer.ui.theme_dialog_ui import Ui_Dialog

try:
    # noinspection PyUnresolvedReferences
    if typing.TYPE_CHECKING:
        from typing import Iterator
except AttributeError:
    pass


# noinspection PyArgumentList
class PluginDialog(QDialog):
    def __init__(self, plugin_dir_path, parent=None):
        # type: (six.string_types, QWidget) -> None
        super(PluginDialog, self).__init__(parent)
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)

        self.theme_model = ThemeItemModel(self)

        # self.ui.list_view_theme.setUniformItemSizes(True)
        self.ui.list_view_theme.setIconSize(QSize(675 // 3, 369 // 3))

        self.thread_obj = LoadingThreadObject(plugin_dir_path)
        self.thread_obj.do()

        for item, thumb_img in self.thread_obj.theme_items:
            # if thumb_img:
            #     item.setIcon(QIcon(QPixmap.fromImage(thumb_img)))
            self.theme_model.add_theme(item)

        self.ui.list_view_theme.setModel(self.theme_model)
        self.sel_model = self.ui.list_view_theme.selectionModel()
        self.sel_model.currentChanged.connect(self._onCurrentChanged)

        # self.ui.text_edit_preview.setOpenLinks(True)
        # self.ui.text_edit_preview.setOpenExternalLinks(True)
        # self.ui.text_edit_preview.setTextInteractionFlags(
        #     self.ui.text_edit_preview.textInteractionFlags() |
        #     Qt.LinksAccessibleByMouse |
        #     Qt.LinksAccessibleByKeyboard
        # )

        self._double_click_done_flag = False

    def set_double_click_done_flag(self, flag):
        # type: (bool) -> None
        self._double_click_done_flag = flag

    def _onCurrentChanged(self, current, _):
        # type: (QModelIndex, QModelIndex) -> None
        self._setup_preview(current)

    @Slot(QModelIndex)
    def on_list_view_theme_doubleClicked(self, index):
        # type: (QModelIndex) -> None
        if index.isValid() and self._double_click_done_flag:
            self.done(self.Accepted)

    def _setup_preview(self, current):
        # type: (QModelIndex) -> None
        item = self.theme_model.itemFromIndex(current)  # type: ThemeItem
        self.ui.text_edit_preview.setMarkdown(item.description, item.text(), thumbnail=item.thumb_path)

    def selectedItems(self):
        # type: () -> [str]
        indexes = self.ui.list_view_theme.selectedIndexes()

        return [
            index.data()
            for index in indexes
            if index.isValid()
        ]


class ThemeItemModel(QStandardItemModel):
    @staticmethod
    def create_item(name, thumb_path, **kwargs):
        # type: (str, str, dict) -> ThemeItem
        return ThemeItem(name, thumb_path, **kwargs)

    def add_theme(self, item):
        self.appendRow(item)


class ThemeItem(QStandardItem):
    def __init__(self, name, thumb_path, **kwargs):
        # type: (str, str, dict) -> None
        super(ThemeItem, self).__init__(name)
        self.thumb_path = thumb_path
        self.description = kwargs.get("description", "").strip()
        self.params = kwargs


class LoadingThreadObject(QObject):
    def __init__(self, path):
        # type: (str) -> None
        super(LoadingThreadObject, self).__init__()
        self.path = path
        self.theme_items = []

    def do(self):
        for root, toml_path in self._toml_walk():
            obj = toml.load(open(toml_path), OrderedDict)

            for theme_name, theme_info in obj.items():
                if "Thumbnail" in theme_info:
                    thumb_path = os.path.join(root, theme_info["Thumbnail"])
                else:
                    thumb_path = os.path.join(root, theme_name + ".png")

                item = ThemeItemModel.create_item(
                    theme_name,
                    thumb_path,
                    **theme_info
                )

                if os.path.isfile(thumb_path):
                    img = QImage(thumb_path)
                else:
                    img = None

                self.theme_items.append((item, img))

    def _toml_walk(self):
        # type: () -> Iterator[(str, str)]
        for root, dirs, files in os.walk(self.path):
            for x in fnmatch.filter(files, "*.toml"):
                yield root, os.path.join(root, x)
