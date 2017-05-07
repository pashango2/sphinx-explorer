#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division, print_function, absolute_import, unicode_literals
import sys
import six
import os
import platform
from qtpy.QtCore import *
from qtpy.QtGui import *
from qtpy.QtWidgets import *

TERM_ENCODING = getattr(sys.stdin, 'encoding', None)

# noinspection PyArgumentList
# QTextCodec.setCodecForCStrings(QTextCodec.codecForLocale())


class QConsoleWidget(QTextEdit):
    started = Signal()
    finished = Signal(int)

    COMMAND_COLOR = QColor("#706caa")
    FINISH_COLOR = QColor("#38b48b")
    ERROR_COLOR = QColor("#eb6ea5")

    # noinspection PyUnresolvedReferences
    def __init__(self, parent=None):
        super(QConsoleWidget, self).__init__(parent)
        self.setReadOnly(True)
        self.setAcceptRichText(True)
        self.queue = []
        self.callback = None

        self._process = QProcess(self)
        self._process.setProcessChannelMode(QProcess.MergedChannels)
        self._process.started.connect(self.started.emit)
        # self._process.finished[int].connect(self._on_finished)
        self._process.finished.connect(self._on_finished)
        self._process.readyReadStandardOutput.connect(self._print_output)
        self._process.readyReadStandardError.connect(self._print_output)

    @staticmethod
    def virtual_env(cwd, venv_path=None, anaconda_name=None):
        if venv_path:
            # Note: QProcess on Windows. Full path only. and add file extension.
            if platform.system() == "Windows":
                if not os.path.abspath(venv_path):
                    venv_path = os.path.join(cwd, venv_path)

            if os.path.isdir(venv_path):
                if platform.system() == "Windows":
                    venv_path = os.path.join(venv_path, "Scripts", "activate.bat")
                else:
                    venv_path = os.path.join(venv_path, "bin", "activate")
            elif os.path.isfile(venv_path):
                if platform.system() == "Windows":
                    if os.path.basename() == "activate":
                        venv_path += ".bat"

            return venv_path

        if anaconda_name:
            if platform.system() == "Linux":
                cmd = "source activate {}".format(anaconda_name)
            else:
                cmd = "activate {}".format(anaconda_name)

            return cmd

        return ""

    def process(self):
        # type: () -> QProcess
        return self._process

    # noinspection PyUnresolvedReferences
    def exec_command(self, cmd, cwd=None, clear=False, callback=None):
        if self._process.state() == QProcess.NotRunning and clear:
            self.clear()

        if cwd:
            if six.PY2:
                cwd = cwd.encode(sys.getfilesystemencoding())
            self._process.setWorkingDirectory(cwd)

        if isinstance(cmd, (list, tuple)):
            self.queue += cmd
        else:
            self.queue += [cmd]

        self.callback = callback

        self.push_cmd()

    def push_cmd(self):
        if not self.queue:
            return

        if QProcess.NotRunning != self._process.state():
            return

        cmd = self.queue.pop(0)
        if six.PY2:
            cmd = cmd.encode(sys.getfilesystemencoding())
            output_cmd = b"> " + cmd + b"\n"
        else:
            output_cmd = "> " + cmd + "\n"

        self._output(output_cmd, self.COMMAND_COLOR)
        self._process.start(cmd)

    @Slot()
    def _print_output(self):
        if self._process is None:
            return

        line = self._process.readAllStandardOutput().data()
        self._output(line)

        line = self._process.readAllStandardError().data()
        self._output(line, self.ERROR_COLOR)

    def _output(self, line, color=None):
        if six.PY3 and isinstance(line, bytes):
            try:
                line = line.decode(sys.getfilesystemencoding())
            except UnicodeDecodeError:
                try:
                    line = line.decode("utf-8")
                except UnicodeDecodeError:
                    line = ""

        self.moveCursor(QTextCursor.End)

        cursor = self.textCursor()
        char_format = QTextCharFormat()
        if color:
            char_format.setForeground(QBrush(color))

        cursor.setCharFormat(char_format)
        cursor.insertText(line)

        self.moveCursor(QTextCursor.End)

    # noinspection PyUnusedLocal
    @Slot(int, QProcess.ExitStatus)
    def _on_finished(self, ret_code, _exit_status):
        if ret_code == 0:
            if self.queue:
                self.push_cmd()
                return
            else:
                if self.callback:
                    self.callback()

        self._output(
            "\nProcess finished with exit code {}".format(ret_code),
            self.FINISH_COLOR if ret_code == 0 else self.ERROR_COLOR
        )

        self.finished.emit(ret_code)

        self.push_cmd()

    def terminate(self):
        if self._process:
            # pid = self._process.pid()
            # os.kill(pid, signal.SIGINT)
            # print("pid", pid)
            # self._process.kill()
            self._process.terminate()
            self._process.waitForFinished()
            self._process = None
