#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
from sphinx_explorer.util import sphinx_config


def test_sphinx_config():
    config_path = os.path.join(os.path.dirname(__file__), "conf", "conf.py")
    # sphinx_config.main(config_path)

    print(sphinx_config.get(config_path))
