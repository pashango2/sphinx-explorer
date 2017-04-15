#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division, print_function, absolute_import, unicode_literals

import ast
import codecs
import os

from six import string_types

from sphinx_explorer.plugin import extension

CONF_PY_ENCODING = "utf-8"


# memo:
# ast -> code module:
#    https://github.com/simonpercivall/astunparse

# noinspection PyMethodMayBeStatic
class MyNodeVisitor(ast.NodeVisitor):
    def __init__(self, source_lines, replace_dict=None):
        # type: ([string_types], dict) -> None
        super(MyNodeVisitor, self).__init__()

        self._source_lines = source_lines[:]
        self.replace_dict = replace_dict or {}

    def visit_Assign(self, node):
        # type: (ast.Assign) -> ast.Assign
        if len(node.targets) == 1:
            left_name = node.targets[0].id

            if left_name in self.replace_dict:
                new_line = "{} = {}\n".format(left_name, repr(self.replace_dict[left_name]))
                self._source_lines[node.lineno - 1] = new_line

        return node

    def visit(self, tree):
        super(MyNodeVisitor, self).visit(tree)
        return self._source_lines


class Parser(object):
    def __init__(self, conf_path):
        self._source = []
        for line in codecs.open(conf_path, "r", CONF_PY_ENCODING).readlines():
            self._source.append(line)

        self._tree = ast.parse(open(conf_path, "r").read())

    def add_sys_path(self, path_list):
        if not path_list:
            return

        insert_sys_flag = False
        new_lines = []
        for line in self._source:
            if line.strip() == "# import os":
                new_lines.append("import os\n")
            elif line.strip() == "# import sys":
                new_lines.append("import sys\n")
            elif "sys.path.insert" in line and insert_sys_flag is False:
                insert_sys_flag = True
                new_lines.append(line)
                for path in path_list:
                    path = "u'" + path + "'"
                    new_lines.append("sys.path.insert(0, os.path.abspath({}))\n".format(path))
            else:
                new_lines.append(line)
        self._source = new_lines
        self._tree = ast.parse(self.dumps().encode(CONF_PY_ENCODING))

    def assign_replace(self, replace_dict):
        self._source = MyNodeVisitor(self._source, replace_dict).visit(self._tree)
        return self._source

    def append(self, line):
        self._source.append(line)

    def dumps(self):
        return "".join(self._source)

    @property
    def lines(self):
        return self._source


def extend_conf_py(conf_py_path, params, extensions=None, insert_paths=None):
    extensions = extensions or []

    if os.path.isfile(conf_py_path):
        parser = Parser(conf_py_path)

        if params:
            parser.assign_replace(params)

        parser.add_sys_path(insert_paths)

        for key in extensions:
            if key.startswith("ext-"):
                ext = extension.get(key)
                if ext and ext.get("conf_py", {}).get("extra_code"):
                    comment = "# -- {} ".format(key)
                    comment += "-" * (75 - len(comment))
                    parser.append("\n\n")
                    parser.append(comment + "\n")
                    parser.append(ext.get("conf_py", {}).get("extra_code"))

        with codecs.open(conf_py_path, "w", CONF_PY_ENCODING) as fd:
            fd.write(parser.dumps())
