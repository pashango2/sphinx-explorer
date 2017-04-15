#!/usr/bin/env python
# -*- coding: utf-8 -*-
import yaml
from sphinx_explorer.plugin.extension import Extension
import sys
import os


def test_extension():
    plugin_text = """
packages: [
    "commonmark",
    "recommonmark"
]

conf_py:
    add_extension: no

    source_suffix: ['.md', "CommonMarkParser"]

    imports:
        - from: recommonmark.parser
          import: CommonMarkParser
        - from: recommonmark.transform
          import: AutoStructify

    extra_code: |
        #from recommonmark.transform import AutoStructify
        github_doc_root = 'https://github.com/rtfd/recommonmark/tree/master/doc/'

        def setup(app):
            app.add_config_value('recommonmark_config', {
                    'url_resolver': lambda url: github_doc_root + url,
                    'auto_toc_tree_section': 'Contents',
                    }, True)
            app.add_transform(AutoStructify)


description: |
    A `docutils`-compatibility bridge to [CommonMark][cm].

"""
    obj = yaml.load(plugin_text)
    ext = Extension(obj)

    assert ext.packages == ["commonmark", "recommonmark"]
    assert ext.extra_code
    assert ext.imports == [
        "from recommonmark.parser import CommonMarkParser",
        "from recommonmark.transform import AutoStructify"
    ]
    assert not ext.add_extensions
    assert ext.source_suffix == ('.md', 'CommonMarkParser')


if __name__ == "__main__":
    import pytest

    pytest.main()
