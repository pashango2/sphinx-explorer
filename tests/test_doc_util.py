#!/usr/bin/env python
# -*- coding: utf-8 -*-
import docutils
import docutils.core


def test_translate():
    rst = """
* This is a bulleted list.
* It has two items, the second
  item uses two lines. (note the indentation)

1. This is a numbered list.
2. It has two items too.

#. This is a numbered list.
#. It has two items too.
    """.strip()

    html = docutils.core.publish_parts(rst, writer_name='html')['html_body']
    print(html)
