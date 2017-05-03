#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division, print_function, absolute_import, unicode_literals
import os
import fnmatch
# noinspection PyPackageRequirements
import yaml
from six import string_types

Extensions = {}
CONF_PY_NUM_INDENT = 4


def init(plugin_dir):
    global Extensions

    for root, dirs, files in os.walk(plugin_dir):
        for file_name in fnmatch.filter(files, "ext-*.yml"):
            ext_name = file_name[:-len(".yml")]
            Extensions[ext_name] = Extension(
                ext_name,
                yaml.load(open(os.path.join(root, file_name))),
                root,
            )


def extensions():
    return Extensions.items()


def get(ext_name):
    return Extensions.get(ext_name)


def list_iter():
    for ext_name, ext in Extensions.items():
        yield ext_name, ext


def dependent_packages():
    for ext_name, ext in Extensions.items():
        for package in ext.packages:
            yield package


class Extension(object):
    # TODO: ast check
    def __init__(self, name, ext_setting, ext_path=None):
        self.name = name
        self.ext_setting = ext_setting
        self.ext_path = ext_path

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
        d = self.conf_py.get("add_extensions")
        if d is None:
            d = self.packages
        elif d is False:
            d = []
        elif isinstance(d, string_types):
            d = [d]

        d = ["'" + x + "'" for x in d]

        return d

    @property
    def exclude_patterns(self):
        return self.conf_py.get("exclude_poatterns", [])

    def has_setting_params(self):
        return bool(self.ext_setting.get("setting_params"))

    @property
    def setting_params(self):
        for ext in self.ext_setting.get("setting_params", []):
            for key, value in ext.items():
                yield key, value

    def generate_py_script(self, params, settings):
        parser = []

        # add imports
        if self.imports:
            for imp in self.imports:
                parser.append(imp)
            parser.append("")

        # add extensions
        if self.add_extensions:
            parser.append("extensions += [")
            for add_ext in self.add_extensions:
                parser.append((" " * CONF_PY_NUM_INDENT) + add_ext + ",")
            parser.append("]")

        # setting params
        for param_name, param_setting in self.setting_params:
            value = params.get(param_name) or settings.get(param_name) or param_setting.get("default")
            if value:
                parser.append("{} = {}".format(param_name, repr(value)))

        # add extra code
        if self.extra_code:
            parser.append(self.extra_code)

        return "\n".join(parser)
