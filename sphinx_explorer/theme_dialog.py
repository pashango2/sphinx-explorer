#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division, print_function, absolute_import, unicode_literals
from PySide.QtGui import *
# from PySide.QtCore import *
from .plugin_dialog import PluginDialog
from .property_widget import RefButtonWidget


ThemePluginDir = "theme_plugin"


class ThemeDialog(PluginDialog):
    def __init__(self, parent=None):
        # type: (QWidget) -> None
        super(ThemeDialog, self).__init__(ThemePluginDir, parent)
        self.set_double_click_done_flag(True)


class HtmlThemeWidget(RefButtonWidget):
    def onRefButtonClicked(self):
        # noinspection PyCallByClass
        dlg = ThemeDialog(self)
        result = dlg.exec_()

        if result == QDialog.Accepted:
            self.line_edit.setText("\n".join(dlg.selectedItems()))
