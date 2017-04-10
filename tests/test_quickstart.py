#!/usr/bin/env python
# -*- coding: utf-8 -*-
from sphinx_explorer import quickstart
import os

sys_path = os.path.join(
    os.path.dirname(__file__),
    "..",
)


def test_build_path():
    d = {u'suffix': u'.rst', u'sep': True, u'prefix': u'_', u'html_theme': u'sphinx_rtd_theme', u'ext-todo': True, u'author': u'Toshiyuki Ishii', u'ext-doctest': True, u'makefile': True, u'master': u'index', u'ext-coverage': True, u'ext-mathjax': True, u'ext-commonmark': True, u'path': u'C:\\Users\\056-kusakabe-n\\Documents\\sphinx-docs\\dsds', u'ext-nbsphinx': True, u'ext-intersphinx': True, u'epub': False, u'ext-viewcode': True, u'language': u'ja', u'ext-githubpage': True, u'ext-ifconfig': True, u'project': u'dsds', u'ext-blockdiag': True, u'batchfile': True, u'ext-fontawesome': True, u'ext-autodoc': True, u'ext-autosummary': True}
    source_dir, build_dir = quickstart.get_source_and_build(d)
    assert source_dir == "source"
    assert build_dir == "build"

    d = {u'sep': False, u'prefix': u'_'}
    source_dir, build_dir = quickstart.get_source_and_build(d)
    assert source_dir == "."
    assert build_dir == "_build"


# def test_question():
#     path = os.path.join(sys_path, "settings", "quickstart.toml")
#     question = quickstart.Questions(path)
#
#     for category in question.categories():
#         print(question.properties(category))


# def test_command():
#     d = {u'ext-imgmath': True, u'ext-coverage': True, u'suffix': u'.rst', u'sep': True, u'ext-commonmark': True,
#          u'ext-mathjax': True, u'prefix': u'_', u'html_theme': u'sphinx_rtd_theme',
#          u'path': u'C:\\test doc', u'batchfile': True, u'ext-nbsphinx': True,
#          u'ext-intersphinx': True, u'epub': False, u'ext-viewcode': True, u'ext-todo': True, u'language': u'ja',
#          u'author': u'Toshiyuki Ishii', u'ext-githubpage': True, u'ext-ifconfig': True, u'ext-doctest': True,
#          u'makefile': True, u'project': u'test doc', u'ext-blockdiag': True, u'version': u'0.1', u'master': u'index',
#          u'ext-fontawesome': True, u'release': u'0.1 rc', u'ext-autodoc': True}
#
#     qs_cmd = quickstart.quickstart_cmd(d)
#
#     print(qs_cmd)
#
