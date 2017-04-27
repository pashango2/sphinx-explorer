#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division, print_function, absolute_import, unicode_literals
from qtpy.QtCore import *
# from qtpy.QtWidgets import *
import re
import logging
from ..util.commander import Commander
logger = logging.getLogger(__name__)


# class Commander(object):
#     def __call__(self, cmd):
#         return cmd


class PipInstallTask(QObject):
    finished = Signal(bool)

    def __init__(self, packages, update_flag=False, commander=Commander(), callback=None, parent=None):
        super(PipInstallTask, self).__init__(parent)
        self.packages = packages or []
        self.callback = callback
        self.commander = commander
        self.update_flag = update_flag

    def run(self):
        result = True
        for package in self.packages:
            update_flag = "-U" if self.update_flag else ""
            ret = self.commander.call("pip install -q {} {}".format(update_flag, package), shell=True)
            if not ret:
                logger.warning("pip failed.")

            result = ret and result

        self.finished.emit(result)


class PipListTask(QObject):
    finished = Signal(list)
    PARSE_RE = re.compile(r"([^\s]+)\s+\(([^\s]+)\)")

    def __init__(self, commander=Commander(), callback=None, parent=None):
        super(PipListTask, self).__init__(parent)
        self.packages = []
        self.callback = callback
        self.commander = commander

    @staticmethod
    def filter(output):
        for line in output.splitlines():
            g = PipListTask.PARSE_RE.match(line)
            if g:
                package, version = g.groups()
                yield package, version

    def run(self):
        self._run()
        self.finished.emit(self.packages)

    def _run(self):
        output = self.commander.check_output("pip list --format=legacy", shell=True)
        if not output:
            logger.warning("pip failed.")
        else:
            for package, version in PipListTask.filter(output):
                self.packages.append((package, version, None))


class PipListOutDateTask(PipListTask):
    OUTDATE_PARSE_RE = re.compile(r"([^\s]+)\s+([^\s]+)\s+([^\s]+)\s+([^\s]+)")

    @staticmethod
    def outdate_filter(output):
        for line in output.splitlines():
            g = PipListOutDateTask.OUTDATE_PARSE_RE.match(line)
            if g:
                package, version, latest, pack_type = g.groups()
                if not package or package[0] == "-" or package == "Package":
                    continue

                yield package, version, latest, pack_type

    def run(self):
        self._run()

        # noinspection PyBroadException
        try:
            output = self.commander.check_output("pip list -o --format=columns", shell=True)
            if not output:
                logger.warning("pip failed.")
        except:
            self.finished.emit(self.packages)
            return

        outdate_package_dict = {}
        for package, version, latest, pack_type in self.outdate_filter(output):
            outdate_package_dict[package] = latest

        new_package = []
        for package, version, _ in self.packages:
            latest = outdate_package_dict.get(package, None)
            new_package.append((package, version, latest))
        self.packages = new_package

        self.finished.emit(self.packages)


