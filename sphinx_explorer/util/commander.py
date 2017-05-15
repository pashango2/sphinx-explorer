#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division, print_function, absolute_import, unicode_literals
import os
import sys
import subprocess
import platform
from six import PY2, string_types
import logging

logger = logging.getLogger(__name__)

TERM_ENCODING = getattr(sys.stdin, 'encoding', None)

if platform.system() == "Windows":
    def quote(s):
        if " " in s:
            return '"' + s + '"'
        return s
else:
    try:
        from shlex import quote
    except ImportError:
        from pipes import quote


def _encoding():
    return TERM_ENCODING or sys.getfilesystemencoding()


class Commander(object):
    def __init__(self, system=platform.system(), py2=PY2):
        self.system = system
        self.py2 = py2
        self.pre_command = [[]]

    def create_pre_commander(self, pre_command=None):
        new_commander = Commander(self.system, self.py2)
        new_commander.pre_command = [pre_command or []]
        return new_commander

    def __call__(self, cmd=None, cwd=None, bash=True, cmds=None):
        new_cmd = []
        _cmds = [cmd] if cmd else []
        _cmds += cmds or []
        for _cmd in self.pre_command + _cmds:
            if isinstance(cmd, (list, tuple)):
                _cmd = [quote(x) for x in _cmd]
                _cmd = " ".join(_cmd)
            new_cmd.append(_cmd)

        new_cmd = [x for x in new_cmd if x]

        if self.system == "Windows":
            cmd_joiner = " & "
        else:
            cmd_joiner = " ; "

        cmd_str = cmd_joiner.join(new_cmd)

        if self.system == "Linux" and bash:
            # cmd_str = cmd_str.replace('"', '\\"').replace("'", "\\'")
            return '/bin/bash -c "{}"'.format(cmd_str)
        else:
            return cmd_str

    def check_exist(self, cmds):
        which_cmd = "which" if platform.system() != "Windows" else "where"
        for cmd in cmds:
            output, _ = self.check_output([which_cmd, cmd], shell=True)

            if output:
                return True

        return False

    def which(self, cmd):
        if self.system == "Windows":
            which_cmd = "where"
        else:
            which_cmd = "which"

        result, _ = self.check_output("{} {}".format(which_cmd, cmd), shell=True)
        if result:
            for line in result.splitlines():
                return line
        return None

    def check_output(self, cmd, shell=False):
        # noinspection PyBroadException
        try:
            p = subprocess.Popen(
                self(cmd),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                stdin=subprocess.PIPE,
                shell=shell
            )
            output, error = p.communicate()
            p.wait()
        except FileNotFoundError:
            logger.error("FileNotFoundError:{}".format(self(cmd)))
            return None, None
        except subprocess.CalledProcessError:
            logger.error("Call Error:{}".format(self(cmd)))
            return None, None
        except:
            import traceback
            logger.warning(traceback.format_exc())
            return None, None

        try:
            output = output.decode(sys.getfilesystemencoding())
        except UnicodeDecodeError:
            logger.error("Unicode Error!!!")
            output = ""

        try:
            error = error.decode(sys.getfilesystemencoding())
        except UnicodeDecodeError:
            logger.error("Unicode Error!!!")
            error = ""

        return output, error

    def call(self, cmd, stderr=None, shell=False):
        try:
            code = subprocess.call(self(cmd), stderr=stderr, shell=shell)
        except FileNotFoundError:
            logger.error("FileNotFoundError:{}".format(self(cmd)))
            return False
        except subprocess.CalledProcessError:
            logger.error("Call Error:{}".format(self(cmd)))
            return False

        return code == 0

    def open_terminal(self, path):
        # type: (string_types) -> None
        cwd = os.path.normpath(path)
        if self.py2:
            cwd = cwd.encode(sys.getfilesystemencoding())

        # noinspection PyBroadException
        try:
            if platform.system() == "Windows":
                subprocess.Popen("cmd", cwd=cwd)
            elif platform.system() == "Darwin":
                subprocess.Popen("open", cwd=cwd)
            else:
                subprocess.Popen("gnome-terminal", cwd=cwd)
        except:
            logger.error("Open Terminal Error.")

    def show_directory(self, path):
        # type: (string_types) -> None
        path = os.path.normpath(path)
        if platform.system() == "Windows":
            cmd = ["explorer", quote(path)]
        elif platform.system() == "Darwin":
            cmd = ["open", quote(path)]
        else:
            cmd = ["xdg-open", quote(path)]
            # print(" ".join(cmd))
        self.launch(" ".join(cmd), path)

    def open(self, path):
        path = os.path.normpath(path)
        if self.system == "Windows":
            cmd = [path]
        elif self.system == "Darwin":
            cmd = ["open", path]
        else:
            cmd = self(["xdg-open", path])
            # print(" ".join(cmd))
        self.launch(cmd)

    @staticmethod
    def launch(cmd, cwd=None):
        # type: (string_types, string_types or None) -> None
        if platform.system() == "Windows":
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.STARTF_USESHOWWINDOW
            if PY2:
                cmd = cmd.encode(_encoding())
                cwd = cwd.encode(sys.getfilesystemencoding()) if cwd else cwd

            subprocess.Popen(
                cmd,
                cwd=cwd,
                shell=True,
                startupinfo=startupinfo
            )
        else:
            subprocess.Popen(
                cmd,
                cwd=cwd,
                shell=True,
                env=os.environ.copy(),
            )

    def console(self, cmd, cwd=None):
        # type: (string_types, string_types) -> None or subprocess.Popen
        if platform.system() == "Windows":
            cmd = self(cmd)
            if PY2:
                cmd = cmd.encode(_encoding())
                cwd = cwd.encode(sys.getfilesystemencoding()) if cwd else cwd

            return subprocess.Popen(
                cmd,
                cwd=cwd,
                creationflags=subprocess.CREATE_NEW_CONSOLE,
            )
        elif platform.system() == "Linux":
            cmd = 'gnome-terminal -e "{}"'.format(self(cmd, bash=False))
            return subprocess.Popen(cmd, cwd=cwd, shell=True)
        else:
            # cmd = command(cmd)
            # subprocess.Popen(cmd, cwd=cwd, shell=True)
            logger.error("Non Impliment")
            return None

    def exec_(self, cmd, cwd=None):
        # type: (string_types, string_types) -> int
        shell = True

        if platform.system() == "Windows":
            cmd = self(('cmd.exe /C "' + cmd + '"'))
            if PY2:
                cmd = cmd.encode(_encoding())
                cwd = cwd.encode(_encoding())

            shell = False
        else:
            cmd = self(cmd)

        p = subprocess.Popen(
            cmd,
            cwd=cwd if cwd else None,
            shell=shell,
        )
        p.wait()
        return p.returncode

    @staticmethod
    def make_command(make_cmd, cwd):
        # type: (string_types, string_types) -> string_types
        if platform.system() == "Windows":
            make_bat = os.path.join(cwd, "make.bat")
            return make_bat + " " + make_cmd
        else:
            return "make " + make_cmd


commander = Commander()
