#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division, print_function, absolute_import, unicode_literals
import sys
from PySide.QtCore import *
from PySide.QtGui import *

TERM_ENCODING = getattr(sys.stdin, 'encoding', None)


class QConsoleWidget(QPlainTextEdit):
    finished = Signal(int, QProcess.ExitStatus)

    def __init__(self, parent=None):
        super(QConsoleWidget, self).__init__(parent)
        self._process = None
        self.setReadOnly(True)

    def process(self):
        # type: () -> QProcess
        return self._process

    def exec_command(self, cmd):
        print(cmd)
        self._process = QProcess(self)
        self._process.readyReadStandardOutput.connect(self._print_output)
        self._process.readyReadStandardError.connect(self._print_output)
        self._process.finished.connect(self.finished)
        self._process.start(cmd)

    @Slot()
    def _print_output(self):
        if self._process is None:
            return

        line = self._process.readAllStandardOutput().data()
        self.moveCursor(QTextCursor.End)
        self.insertPlainText(line.decode(TERM_ENCODING))
        self.moveCursor(QTextCursor.End)

    def terminate(self):
        if self._process:
            pid = self._process.pid()
            # os.kill(pid, signal.SIGINT)
            # print("pid", pid)
            # self._process.kill()
            self._process.terminate()
            self._process.waitForFinished()
            self._process = None