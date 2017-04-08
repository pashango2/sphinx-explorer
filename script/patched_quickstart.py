#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division, print_function, absolute_import, unicode_literals
import sys
import os
import codecs
from sphinx import quickstart


org_generate = quickstart.generate
TEMPLATE_SETTING = """
source_dir = '{rsrcdir}'
build_dir = '{rbuilddir}'
""".strip()


def generate(d, overwrite=True, silent=False, templatedir=None):
    org_generate(d, overwrite, silent, templatedir)

    fd = codecs.open(os.path.join(d["path"], "setting.toml"), "w", "utf-8")
    fd.write(TEMPLATE_SETTING.format(**d))
    fd.close()


def main(argv):
    quickstart.TERM_ENCODING = quickstart.TERM_ENCODING or sys.getfilesystemencoding()
    quickstart.generate = generate
    quickstart.main(argv)


if __name__ == "__main__":
    main(sys.argv)
    sys.exit(0)
