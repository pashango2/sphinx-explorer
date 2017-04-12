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
    started = Signal()
    finished = Signal(int)

    COMMAND_COLOR = QColor("#706caa")

    def __init__(self, parent=None):
        super(QConsoleWidget, self).__init__(parent)
        self.setReadOnly(True)
        self.setAcceptRichText(True)

        self._process = QProcess(self)
        self._process.setProcessChannelMode(QProcess.MergedChannels)
        self._process.started.connect(self.started.emit)
        self._process.finished[int].connect(self.finished.emit)
        self._process.readyReadStandardOutput.connect(self._print_output)
        self._process.readyReadStandardError.connect(self._print_output)

    def process(self):
        # type: () -> QProcess
        return self._process

    # noinspection PyUnresolvedReferences
    def exec_command(self, cmd, cwd=None):
        if cwd:
            if six.PY2:
                cwd = cwd.encode(sys.getfilesystemencoding())
            self._process.setWorkingDirectory(cwd)

        if six.PY2:
            cmd = cmd.encode(sys.getfilesystemencoding())

        self._output("> " + cmd + "\n", self.COMMAND_COLOR)
        self._process.start(cmd)

    @Slot()
    def _print_output(self):
        if self._process is None:
            return

        line = self._process.readAllStandardOutput().data()
        self._output(line)

        line = self._process.readAllStandardError().data()
        self._output(line, Qt.red)

    def _output(self, line, color=None):
        if six.PY3 and isinstance(line, bytes):
            line = line.decode(sys.getfilesystemencoding())

        self.moveCursor(QTextCursor.End)

        cursor = self.textCursor()
        char_format = QTextCharFormat()
        if color:
            char_format.setForeground(QBrush(color))
        cursor.setCharFormat(char_format)
        cursor.insertText(line)

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
