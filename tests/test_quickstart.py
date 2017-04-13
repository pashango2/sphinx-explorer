#!/usr/bin/env python
# -*- coding: utf-8 -*-
from sphinx_explorer import quickstart, apidoc
import os
import toml

sys_path = os.path.join(
    os.path.dirname(__file__),
    "..",
)


def test_api_doc(tmpdir):
    cmd = apidoc.create_command(str(tmpdir), "..", {})
    os.system(cmd)
    apidoc.fix_apidoc(str(tmpdir), "..", {})
    setting = toml.load(os.path.join(str(tmpdir), "setting.toml"))
    assert setting["build_dir"] in os.listdir(str(tmpdir))


def test_quickstart(tmpdir):
    temp_dir = str(tmpdir)
    params = {
        "project": "xxx",
        "author": "a",
        "path": temp_dir,
    }
    cmd = quickstart.quickstart_cmd(params)
    print(cmd)
    os.system(cmd)
    print(os.listdir(temp_dir))


def check_build_path(temp_dir, d, build_dir):
    cmd = quickstart.quickstart_cmd(d)
    os.system(cmd)

    assert build_dir in os.listdir(temp_dir)


def test_build_path(tmpdir):
    temp_dir = str(tmpdir)
    d = {u'suffix': u'.rst', u'sep': True, u'prefix': u'_', u'html_theme': u'sphinx_rtd_theme', u'ext-todo': True,
         u'author': u'Toshiyuki Ishii', u'ext-doctest': True, u'makefile': True, u'master': u'index',
         u'ext-coverage': True, u'ext-mathjax': True, u'ext-commonmark': True,
         u'path': temp_dir, u'ext-nbsphinx': True,
         u'ext-intersphinx': True, u'epub': False, u'ext-viewcode': True, u'language': u'ja', u'ext-githubpage': True,
         u'ext-ifconfig': True, u'project': u'dsds', u'ext-blockdiag': True, u'batchfile': True,
         u'ext-fontawesome': True, u'ext-autodoc': True, u'ext-autosummary': True}
    source_dir, build_dir = quickstart.get_source_and_build(d)
    assert source_dir == "source"
    check_build_path(temp_dir, d, build_dir)


def test_build_path2(tmpdir):
    temp_dir = str(tmpdir)
    d = {u'sep': False, u'prefix': u'_', "path": temp_dir, "project": "x", "author": "x"}
    source_dir, build_dir = quickstart.get_source_and_build(d)
    assert source_dir == "."
    check_build_path(temp_dir, d, build_dir)


