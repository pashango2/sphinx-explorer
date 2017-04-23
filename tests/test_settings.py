#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
from sphinx_explorer.system_settings import SystemSettings

path = os.path.join(
    os.path.dirname(__file__),
    "settings",
    "settings.toml"
)


def test_settings():
    settings = SystemSettings(path)
    print(settings)


def test_default_settings():
    settings = SystemSettings(None)
    print(settings)