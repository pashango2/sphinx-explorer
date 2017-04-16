#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division, print_function, absolute_import, unicode_literals
import sys
import os
from PySide.QtGui import *
from sphinx_explorer.util.QConsoleWidget import QConsoleWidget

try:
    app = QApplication(sys.argv)
except RuntimeError:
    pass

here = os.path.dirname(__file__)
script_path = os.path.join(here, "process_script.py")


def test_encoding():
    widget = QConsoleWidget()

    cmd = [
        "python",
        script_path,
    ]
    widget.exec_command(" ".join(cmd), cwd=here)
    process = widget.process()
    ret_code = process.waitForFinished()
    assert True is ret_code
    assert widget.toPlainText()

    cmd = [
        "python",
        script_path,
        "日本語",
    ]
    widget.clear()
    widget.exec_command(" ".join(cmd), cwd=here)
    process = widget.process()
    ret_code = process.waitForFinished()
    assert True is ret_code
    print("--", widget.toPlainText())
    # assert widget.toPlainText()
    print(widget.toPlainText())


if __name__ == "__main__":
    import pytest
    pytest.main()
