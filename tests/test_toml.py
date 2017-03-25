#!/usr/bin/env python
# -*- coding: utf-8 -*-
import toml


def test_toml():
    text = """
description = '''
html_theme = "rtd_theme"
'''
    """.strip()

    obj = toml.loads(text)
    print(obj["description"])

    text = """
lines = '''
The first newline is
trimmed in raw strings.
   'All other whitespace'
   is preserved.
'''
""".strip()

    obj = toml.loads(text)
    print(obj)

