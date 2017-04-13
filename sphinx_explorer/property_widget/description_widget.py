#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division, print_function, absolute_import, unicode_literals
# from six import string_types
# from PySide.QtCore import *
from PySide.QtGui import *
import markdown

CssStyle = """
<style>
a {color: #4183C4; }
a.absent {color: #cc0000; }
a.anchor {
  display: block;
  padding-left: 30px;
  margin-left: -30px;
  cursor: pointer;
  position: absolute;
  top: 0;
  left: 0;
  bottom: 0; }

</style>
"""


class DescriptionWidget(QTextBrowser):
    FONT_POINT_SIZE = 12

    def __init__(self, parent=None):
        super(DescriptionWidget, self).__init__(parent)
        font = QFont()
        font.setPointSize(self.FONT_POINT_SIZE)
        self.setFont(font)

        self.setOpenExternalLinks(True)

    def setMarkdown(self, description, title=None, title_prefix="#", thumbnail=None, search_path=None):
        if search_path:
            self.setSearchPaths([search_path])
        else:
            self.setSearchPaths([])

        md = []
        if title:
            md.append("{} {}".format(title_prefix, title))

        md.append(description)

        if thumbnail:
            md.append("![thumbnail]({})".format(thumbnail))

        mdo = markdown.Markdown(extensions=["gfm"])
        html = CssStyle + mdo.convert("\n".join(md))
        self.setHtml(html)
