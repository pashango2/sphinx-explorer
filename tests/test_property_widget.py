#!/usr/bin/env python
# -*- coding: utf-8 -*-
from sphinx_explorer.property_widget import PropertyWidget
import sys
import os
from PySide.QtCore import *
from PySide.QtGui import *

try:
    app = QApplication(sys.argv)
except RuntimeError:
    pass


def test_property_widget():
    widget = PropertyWidget()

    settings = {
        "name": {
            "name": "name",
        },
        "path": {
            "name": "path",
            "default": ".",
            "link": "name",
            "link_format": "{_default}{_path_sep}{}",
        },
    }
    props = widget.load_settings(settings)
    assert len(props) == 2

    props_d = {x.text(): x for x in props}

    model = widget.model()
    model.setData(model.index(props_d["name"].index().row(), 1), "test")
    assert props_d["path"].value == os.path.join(".", "test")

    obj = widget.dump()
    assert obj == {'path': './test', 'name': 'test'}


def test_add_item():
    widget = PropertyWidget()
    widget.add_property(
        "name", value="test"
    )

    obj = widget.dump()
    assert obj == {"name": "test"}


if __name__ == "__main__":
    import pytest
    pytest.main()
