#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division, print_function, absolute_import, unicode_literals
# from six import string_types
import sys
import os
import markdown

from qtpy.QtCore import *
from qtpy.QtGui import *

USE_WEB_ENGINE = True

if USE_WEB_ENGINE:
    from qtpy.QtWebEngineWidgets import QWebEngineView, QWebEngineSettings
    BASE_CLASS = QWebEngineView
else:
    from qtpy.QtWidgets import *
    BASE_CLASS = QTextBrowser


# noinspection PyArgumentList
class DescriptionWidget(BASE_CLASS):
    FONT_POINT_SIZE = 12
    SetupFlag = False
    CssStyle = ""

    @staticmethod
    def setup():
        if USE_WEB_ENGINE:
            QWebEngineSettings.globalSettings().setAttribute(
                QWebEngineSettings.PluginsEnabled,
                True
            )

            here = os.path.dirname(sys.argv[0])
            css_path = os.path.join(here, "css", "markdown-dark-material.css")

            DescriptionWidget.CssStyle = """
<style>
{}
</style>
<body class="vscode-dark">
            """.format(open(css_path).read())
        else:
            DescriptionWidget.CssStyle = """
<style>

body{
    margin: 10px;
}
a{
    color:#4080d0;
    text-decoration:none;
}
h1 {
    margin-bottom: 20px;
    margin-top: 50px;
    padding-top: 50px;
}
h3 {
    margin-bottom: 50px;
    padding-bottom: 50px;
}

table {
    background-color: #FFFFFF;
    margin-top: 10px;
}

th {
    background-color: #006e54;
    padding: 7px;
}

td {
   padding-right: 30px;
   background-color: #232629;
   padding: 7px;
}

</style>
"""

        DescriptionWidget.SetupFlag = True

    def __init__(self, parent=None):
        if not DescriptionWidget.SetupFlag:
            self.setup()

        super(DescriptionWidget, self).__init__(parent)
        font = QFont()
        font.setPointSize(self.FONT_POINT_SIZE)
        self.setFont(font)

        if USE_WEB_ENGINE:
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
        if USE_WEB_ENGINE:
            html = self.CssStyle + mdo.convert("\n".join(md)) + "</body>"
        else:
            html = self.CssStyle + "<body>" + mdo.convert("\n".join(md)) + "</body>"

        if USE_WEB_ENGINE:
            if search_path:
                # noinspection PyTypeChecker
                base_url = QUrl.fromLocalFile(os.path.join(search_path, "index.html"))
                self.setHtml(html, base_url)
            else:
                self.setHtml(html)
        else:
            if search_path:
                self.setSearchPaths([search_path])

            self.setHtml(html)
