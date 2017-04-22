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


class PipListTask(QObject):
    finished = Signal()
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
        output = self.commander.check_output("pip list --format=legacy", shell=True)
        if not output:
            logger.warning("pip failed.")

        for package, version in PipListTask.filter(output):
            self.packages.append((package, version))

        self.finished.emit()


class PipListOutDateTask(QObject):
    finished = Signal()
    PARSE_RE = re.compile(r"([^\s]+)\s+([^\s]+)\s+([^\s]+)\s+([^\s]+)")

    def __init__(self, commander=Commander(), callback=None, parent=None):
        super(PipListOutDateTask, self).__init__(parent)
        self.packages = []
        self.callback = callback
        self.commander = commander

    @staticmethod
    def filter(output):
        for line in output.splitlines():
            g = PipListOutDateTask.PARSE_RE.match(line)
            if g:
                package, version, latest, pack_type = g.groups()
                if not package or package[0] == "-" or package == "Package":
                    continue

                yield package, version, latest, pack_type

    def run(self):
        output = self.commander.check_output("pip list -o --format=columns", shell=True)
        if not output:
            logger.warning("pip failed.")

        for package, version, latest, pack_type in self.filter(output):
            self.packages.append((package, version, latest, pack_type))

        self.finished.emit()
