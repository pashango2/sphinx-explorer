#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division, print_function, absolute_import, unicode_literals
from qtpy.QtCore import *
# from qtpy.QtWidgets import *
import re
import logging
from sphinx_explorer.util.commander import Commander
logger = logging.getLogger(__name__)


# class Commander(object):
#     def __call__(self, cmd):
#         return cmd


class PipInstallTask(QObject):
    finished = Signal(bool, str, str)

    def __init__(self, packages, update_flag=False, commander=Commander(), callback=None, parent=None):
        super(PipInstallTask, self).__init__(parent)
        self.packages = packages or []
        self.callback = callback
        self.commander = commander
        self.update_flag = update_flag

    def run(self):
        for package in self.packages:
            update_flag = "-U" if self.update_flag else ""
            result = self.commander.call("pip install -q {} {}".format(update_flag, package), shell=True)
            if not result:
                logger.warning("pip failed.")

            package_info = self.commander.check_output("pip show {}".format(package), shell=True)
            version = self.get_version(package_info)

            self.finished.emit(True, package, version)

    @staticmethod
    def get_version(msg):
        if not msg:
            return None

        for line in msg.splitlines():
            if line.startswith("Version: "):
                version = line[len("Version: "):].strip()
                break
        else:
            version = None

        return version


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
                yield package, version, None

    def run(self):
        self._run()
        self.finished.emit(self.packages)

    def _run(self):
        output = self.commander.check_output("pip list --format=legacy", shell=True)
        if not output:
            logger.warning("pip failed.")
        else:
            for package, version, latest in PipListTask.filter(output):
                self.packages.append((package, version, latest))


class PipListOutDateTask(PipListTask):
    OUTDATE_PARSE_RE = re.compile(r"([^\s]+)\s+([^\s]+)\s+([^\s]+)\s+([^\s]+)")

    @staticmethod
    def outdate_filter(output):
        if not output:
            return

        for line in output.splitlines():
            g = PipListOutDateTask.OUTDATE_PARSE_RE.match(line)
            if g:
                package, version, latest, pack_type = g.groups()
                if not package or package[0] == "-" or package == "Package":
                    continue

                yield package, version, latest, pack_type

    def run(self):
        # noinspection PyBroadException
        try:
            output = self.commander.check_output("pip list -o --format=columns", shell=True)
            if not output:
                logger.warning("pip failed.")
        except:
            self.finished.emit(self.packages)
            return

        for package, version, latest, _ in self.outdate_filter(output):
            self.packages.append((package, version, latest))

        self.finished.emit(self.packages)


