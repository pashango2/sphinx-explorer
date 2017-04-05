#!/usr/bin/env python
# -*- coding: utf-8 -*-
from sphinx_explorer import quickstart
import os

sys_path = os.path.join(
    os.path.dirname(__file__),
    "..",
)


def test_question():
    path = os.path.join(sys_path, "settings", "quickstart.toml")
    question = quickstart.Questions(path)

    for category in question.categories():
        print(question.properties(category))


def test_command():
    d = {u'ext-imgmath': True, u'ext-coverage': True, u'suffix': u'.rst', u'sep': True, u'ext-commonmark': True,
         u'ext-mathjax': True, u'prefix': u'_', u'html_theme': u'sphinx_rtd_theme',
         u'path': u'C:\\test doc', u'batchfile': True, u'ext-nbsphinx': True,
         u'ext-intersphinx': True, u'epub': False, u'ext-viewcode': True, u'ext-todo': True, u'language': u'ja',
         u'author': u'Toshiyuki Ishii', u'ext-githubpage': True, u'ext-ifconfig': True, u'ext-doctest': True,
         u'makefile': True, u'project': u'test doc', u'ext-blockdiag': True, u'version': u'0.1', u'master': u'index',
         u'ext-fontawesome': True, u'release': u'0.1 rc', u'ext-autodoc': True}

    qs_cmd = quickstart.quickstart_cmd(d)

    print(qs_cmd)

