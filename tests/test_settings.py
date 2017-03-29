#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
from sphinx_explorer.settings import Settings

path = os.path.join(
    os.path.dirname(__file__),
    "settings",
    "settings.toml"
)


def test_settings():
    settings = Settings(path)
    print(settings)
