#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division, print_function, absolute_import, unicode_literals

import codecs
import os
from . import extension

CONF_PY_ENCODING = "utf-8"


def extend_conf_py(source_dir, extensions=None, html_theme=None):
    conf_py_path = os.path.join(source_dir, "conf.py")
    extensions = extensions or []
    print(conf_py_path, os.path.isfile(conf_py_path))

    if os.path.isfile(conf_py_path):
        fd = codecs.open(conf_py_path, "a", CONF_PY_ENCODING)

        if html_theme:
            fd.write("html_theme = '{}'\n".format(html_theme))

        for key in extensions:
            if key.startswith("ext-"):
                ext = extension.get(key)
                if ext and hasattr(ext, "conf_py"):
                    comment = "# -- {} ".format(key)
                    comment += "-" * (75 - len(comment))
                    fd.write("\n\n")
                    fd.write(comment + "\n")
                    fd.write(ext.conf_py)

        fd.close()
