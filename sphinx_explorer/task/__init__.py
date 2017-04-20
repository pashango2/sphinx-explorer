#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division, print_function, absolute_import, unicode_literals
from PySide.QtCore import *
from ..system_settings import *


class SystemInitTask(QObject, QRunnable):
    finished = Signal(object)

    def __init__(self, parent=None):
        # type: () -> None
        QObject.__init__(self, parent)
        QRunnable.__init__(self)

    def run(self):
        result = {}
        print("task")
        self.finished.emit(result)