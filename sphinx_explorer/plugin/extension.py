#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division, print_function, absolute_import, unicode_literals
import sys
import os
import fnmatch
import yaml

Extensions = {}


def init(plugin_dir):
    global Extensions

    sys.path.insert(0, plugin_dir)

    Extensions = {}
    for root, dirs, files in os.walk(plugin_dir):
        for file_name in fnmatch.filter(files, "ext-*.yml"):
            ext_name = file_name[:-len(".yml")]
            Extensions[ext_name] = Extension(yaml.load(open(os.path.join(root, file_name))))


def get(ext_name):
    return Extensions.get(ext_name)


def list_iter():
    for ext_name, ext in Extensions.items():
        yield ext_name, ext


class Extension(object):
    # TODO: ast check
    def __init__(self, ext_setting):
        self.ext_setting = ext_setting

    @property
    def description(self):
        return self.ext_setting.get("description")

    @property
    def extra_code(self):
        conf_py = self.ext_setting.get("conf_py")
        if conf_py:
            return conf_py.get("extra_code")
        return None

    @property
    def packages(self):
        return self.ext_setting.get("packages", [])

    @property
    def conf_py(self):
        return self.ext_setting.get("conf_py", {})

    @property
    def imports(self):
        ret = []
        for imp in self.conf_py.get("imports", []):
            if "from" in imp:
                ret.append("from {} import {}".format(imp["from"], imp["import"]))
            else:
                ret.append("import {}".format(imp["import"]))
        return ret

    @property
    def source_suffix(self):
        ext, parser = self.conf_py.get("source_suffix", (None, None))
        if ext and parser:
            return ext, parser
        return ()

    @property
    def add_extensions(self):
        d = self.conf_py.get("add_extension")
        if d is None:
            return self.packages
        if d is False:
            return []
        return d
