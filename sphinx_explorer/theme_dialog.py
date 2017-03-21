#!/usr/bin/env python
# -*- coding: utf-8 -*-
from PySide.QtGui import *
from PySide.QtCore import *
import os
import json
import markdown
import fnmatch
from .theme_dialog_ui import Ui_Dialog


ThemePluginDir = "theme_plugin"


class ThemeDialog(QDialog):
    def __init__(self, parent=None):
        super(ThemeDialog, self).__init__(parent)
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)

        self.theme_model = ThemeItemModel(self)

        # self.ui.list_view_theme.setUniformItemSizes(True)
        self.ui.list_view_theme.setIconSize(QSize(675//3, 369//3))

        self.thread_obj = LoadingThreadObject(ThemePluginDir)
        self.thread_obj.do()

        for item, thumb_img in self.thread_obj.theme_items:
            if thumb_img:
                item.setIcon(QIcon(QPixmap.fromImage(thumb_img)))
            self.theme_model.add_theme(item)

        self.ui.list_view_theme.setModel(self.theme_model)
        self.sel_model = self.ui.list_view_theme.selectionModel()
        self.sel_model.currentChanged.connect(self._onCurrentChanged)

        self.ui.text_edit_preview.setOpenLinks(True)
        self.ui.text_edit_preview.setOpenExternalLinks(True)
        self.ui.text_edit_preview.setTextInteractionFlags(
            self.ui.text_edit_preview.textInteractionFlags() |
            Qt.LinksAccessibleByMouse |
            Qt.LinksAccessibleByKeyboard
        )

    def _onCurrentChanged(self, current, prev):
        self._setup_preview(current)

    def _setup_preview(self, current):
        # type: (QModelIndex) -> None
        item = self.theme_model.itemFromIndex(current)

        md = """
# {}

its makdown

## test

[test](http://google.co.jp)

![]({})
        """.strip().format(item.text(), item.thumb_path)

        mdo = markdown.Markdown()
        self.ui.text_edit_preview.setHtml(mdo.convert(md))


class ThemeItemModel(QStandardItemModel):
    @staticmethod
    def create_item(name, thumb_path, **kwargs):
        # type: (str, str) -> ThemeItem
        return ThemeItem(name, thumb_path, **kwargs)

    def add_theme(self, item):
        self.appendRow(item)


class ThemeItem(QStandardItem):
    def __init__(self, name, thumb_path, **kwargs):
        super(ThemeItem, self).__init__(name)
        self.thumb_path = thumb_path


class LoadingThreadObject(QObject):
    def __init__(self, path):
        # type: (str) -> None
        super(LoadingThreadObject, self).__init__()
        self.path = path
        self.theme_items = []

    def do(self):
        for root, json_path in self._json_walk():
            obj = json.load(open(json_path))

            if isinstance(obj, dict):
                obj = [obj]

            for theme_info in obj:
                if "Thumbnail" in theme_info:
                    thumb_path = os.path.join(root, theme_info["Thumbnail"])
                else:
                    thumb_path = os.path.join(root, theme_info["Name"] + ".png")

                item = ThemeItemModel.create_item(
                    theme_info.get("Name"),
                    thumb_path,
                    **theme_info
                )

                if os.path.isfile(thumb_path):
                    img = QImage(thumb_path)
                else:
                    img = None

                self.theme_items.append((item, img))

    def _json_walk(self):
        # type: () -> Iterator[(str, str)]
        for root, dirs, files in os.walk(self.path):
            for x in fnmatch.filter(files, "*.json"):
                yield root, os.path.join(root, x)
