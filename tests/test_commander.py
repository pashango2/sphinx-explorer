#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division, print_function, absolute_import, unicode_literals
from sphinx_explorer.util.commander import Commander
import platform


def test_python_mode():
    commander = Commander(system="Linux", py2=False)

    c = commander(["python", "/test path"])

    if platform.system() == "Linux":
        assert c == "/bin/bash -c \"python '/test path'\""


if __name__ == "__main__":
    import pytest

    pytest.main()
