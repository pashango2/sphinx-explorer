#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division, print_function, absolute_import, unicode_literals
import sys


print("stdin:", sys.stdin.encoding)
print("stdout:", sys.stdout.encoding)
print("stderr:", sys.stderr.encoding)
if sys.argv[1:]:
    print("--")

    print("arg:", sys.argv[1])
    text = unicode(sys.argv[1], "cp932")
    print(text == "日本語")
    print(text.encode("cp932"))
