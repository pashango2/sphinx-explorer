#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division, print_function, absolute_import, unicode_literals
import os
import toml
import yaml
from sphinx_explorer.property_widget import PropertyWidget, PropertyModel


def pytest_funcarg__params_dict(request):
    path = os.path.join("..", "..", "settings", "params.toml")
    params_dict = toml.load(path)

    return params_dict


def pytest_funcarg__simple_model(request):
    model = PropertyModel()
    settings = """
- "# categoryA"
-
    - a
    - b
    - c
- "# Link"
-
    - d:
        link: a
    """.strip()

    setting_obj = yaml.load(settings)
    model.load_settings(setting_obj)

    return model