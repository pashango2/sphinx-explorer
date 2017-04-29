#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division, print_function, absolute_import, unicode_literals
from qtpy.QtCore import *

from sphinx_explorer.python_venv.package_model import PackageModel, PackageItem
from .plugin import extension
from .python_venv import PipInstallTask, Env
from .util.commander import commander
from .task import push_task

import logging
logger = logging.getLogger(__name__)
package_dict = {}
g_parent = None

if False:
    from typing import Tuple


def init(parent):
    global g_parent
    g_parent = parent


def get_model(python_env):
    # type: (Env) -> SphinxPackageModel
    global package_dict, g_parent

    path = python_env.python_path()

    if path not in package_dict:
        model = SphinxPackageModel(python_env, g_parent)
        package_dict[path] = model
    else:
        model = package_dict[path]

    return model


class SphinxPackageModel(PackageModel):
    loadingStateChanged = Signal(bool)

    def __init__(self, python_env, parent=None):
        # type; (Env, QWidget) -> None
        super(SphinxPackageModel, self).__init__(parent)
        self.python_env = python_env
        self.was_loaded = False

        activate_command = python_env.activate_command()
        self.commander = commander.create_pre_commander(activate_command)

    def load(self, packages):
        # type: ([Tuple[str, str, str]]) -> None
        new_packages = []
        dependent_packages = [PackageModel.package_name_filter(x) for x in extension.dependent_packages()]
        dependent_packages += ["sphinx", "sphinx-rtd-theme"]
        package_names = []

        for package, version, latest in packages:
            package = PackageModel.package_name_filter(package)
            if package.startswith("sphinx-") or package.startswith("sphinxcontrib-") or \
               package in dependent_packages:
                new_packages.append((package, version, latest))
                package_names.append(package)

        # not dependent
        for non_installed_package in (set(dependent_packages) - set(package_names)):
            new_packages.append((non_installed_package, None, None))

        super(SphinxPackageModel, self).load(new_packages)
        self.was_loaded = True

        self.loadingStateChanged.emit(self.was_loaded)

    def update(self, packages):
        # type: ([Tuple[str, str, str]]) -> None
        for package, version, latest in packages:
            package_item = self.find(package)
            if package_item:
                package_item.version = version
                package_item.latest = latest

                index = package_item.index()
                right_index = index.sibling(index.row(), self.rowCount() - 1)
                # noinspection PyUnresolvedReferences
                self.dataChanged.emit(index, right_index)

    def install(self, package_item):
        # type: (PackageItem) -> None
        if package_item.version:
            logger.warning("{} is already installed.".format(package_item.package))
            return

        package_item.installing = True

        task = PipInstallTask([package_item.package], commander=self.commander)
        task.finished.connect(self._on_install_finished)
        push_task(task)

    def _on_install_finished(self, _, package_name, version):
        package_item = self.find(package_name)
        if package_item is None:
            logger.warning("{} is not found".format(package_name))
            return

        package_item.installing = False
        package_item.version = version
        package_item.update_color()

        index = package_item.index()
        right_index = index.sibling(index.row(), self.rowCount() - 1)
        # noinspection PyUnresolvedReferences
        self.dataChanged.emit(index, right_index)
