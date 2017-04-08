#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division, print_function, absolute_import, unicode_literals
import sys
import six
from PySide.QtCore import *
from PySide.QtGui import *

TERM_ENCODING = getattr(sys.stdin, 'encoding', None)

# noinspection PyArgumentList
QTextCodec.setCodecForCStrings(QTextCodec.codecForLocale())


class QConsoleWidget(QTextEdit):
    finished = Signal(int, QProcess.ExitStatus)

    def __init__(self, parent=None):
        super(QConsoleWidget, self).__init__(parent)
        self._process = QProcess(self)
        self.setReadOnly(True)

    def process(self):
        # type: () -> QProcess
        return self._process

    # noinspection PyUnresolvedReferences
    def exec_command(self, cmd, cwd=None):
        if cwd:
            if six.PY2:
                cwd = cwd.encode(sys.getfilesystemencoding())
            self._process.setWorkingDirectory(cwd)

        self._process.readyReadStandardOutput.connect(self._print_output)
        self._process.readyReadStandardError.connect(self._print_output)
        self._process.finished.connect(self.finished)
        if six.PY2:
            cmd = cmd.encode(sys.getfilesystemencoding())
        self._process.start(cmd)

    @Slot()
    def _print_output(self):
        if self._process is None:
            return

        line = self._process.readAllStandardOutput().data()
        self.moveCursor(QTextCursor.End)
        if six.PY3:
            line = line.decode(sys.getfilesystemencoding())
        self.append(line)
        self.moveCursor(QTextCursor.End)

    def terminate(self):
        if self._process:
            # pid = self._process.pid()
            # os.kill(pid, signal.SIGINT)
            # print("pid", pid)
            # self._process.kill()
            self._process.terminate()
            self._process.waitForFinished()
            self._process = None
