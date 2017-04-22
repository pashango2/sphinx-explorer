#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division, print_function, absolute_import, unicode_literals
# from six import string_types
import sys
import os
from qtpy.QtCore import *
from qtpy.QtGui import *
# from qtpy.QtWidgets import *
from qtpy.QtWebEngineWidgets import QWebEngineView, QWebEngineSettings
# from PySide.QtWebKit import QWebView
import markdown


class DescriptionWidget(QWebEngineView):
    FONT_POINT_SIZE = 12
    SetupFlag = False
    CssStyle = ""

    @staticmethod
    def setup():
        QWebEngineSettings.globalSettings().setAttribute(QWebEngineSettings.PluginsEnabled, True)

        here = os.path.dirname(sys.argv[0])
        css_path = os.path.join(here, "css", "github-markdown.css")

        DescriptionWidget.CssStyle = """
        <style>
        {}
        .markdown-body {{
            background: #232629;
            color: #FFFFFF;
        }}

        .markdown-body .highlight pre,
        .markdown-body pre {{
          background-color: #474a4d;
        }}

        .markdown-body a {{
          color: #a0d8ef;
          text-decoration: none;
        }}

        .markdown-body img {{
          background-color: #dcdddd;
        }}

        </style>
        <body class="markdown-body">
        """.format(open(css_path).read())

        DescriptionWidget.SetupFlag = True

    def __init__(self, parent=None):
        if not DescriptionWidget.SetupFlag:
            self.setup()

        super(DescriptionWidget, self).__init__(parent)
        font = QFont()
        font.setPointSize(self.FONT_POINT_SIZE)
        self.setFont(font)

        page = self.page()
        page.setBackgroundColor(Qt.transparent)

    def clear(self):
        pass

    def setMarkdown(self, description, title=None, title_prefix="#", thumbnail=None, search_path=None):
        md = []
        if title:
            md.append("{} {}".format(title_prefix, title))

        md.append(description)

        if thumbnail:
            md.append("![thumbnail]({})".format(thumbnail))

        mdo = markdown.Markdown(extensions=["gfm"])
        html = self.CssStyle + mdo.convert("\n".join(md)) + "</body>"

        if search_path:
            base_url = QUrl.fromLocalFile(os.path.join(search_path, "index.html"))
            self.setHtml(html, base_url)
        else:
            self.setHtml(html)

