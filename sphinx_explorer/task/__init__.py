#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division, print_function, absolute_import, unicode_literals

import logging

from qtpy.QtCore import *

from sphinx_explorer.python_venv import PythonVEnv
from ..python_venv import PipListTask, PipListOutDateTask, Env
from ..util.commander import commander

logger = logging.getLogger(__name__)


class BaseTask(QObject):
    messaged = Signal(str, int)

    def __init__(self, parent=None):
        # type: () -> None
        super(BaseTask, self).__init__(parent)

    def message(self, msg, timeout=3000):
        self.messaged.emit(msg, timeout)


class SystemInitTask(BaseTask):
    checkPythonEnvFinished = Signal(PythonVEnv)
    checkPythonPackageFinished = Signal(Env, list)
    checkLatestPackageFinished = Signal(Env, list)

    finished = Signal(PythonVEnv)

    def __init__(self, settings, parent=None):
        # type: () -> None
        super(SystemInitTask, self).__init__(parent)
        self.settings = settings

    def run(self):
        self.message("Checking Python Venv...", 0)
        env = PythonVEnv.create_system_python_env(self.settings.venv_setting())

        self.message("Checking Python Venv Finished")
        self.checkPythonEnvFinished.emit(env)

        self.message("Checking Python Packages...", 0)
        for key, e in env.env_list():
            activate_commander = commander.create_pre_commander(e.activate_command())

            task = PipListTask(commander=activate_commander)
            task.run()
            self.checkPythonPackageFinished.emit(e, task.packages)
        self.message("Check Python Package Finished")

        self.message("Checking Latest Python Packages...", 0)
        for key, e in env.env_list():
            activate_commander = commander.create_pre_commander(e.activate_command())

            task = PipListOutDateTask(commander=activate_commander)
            task.run()
            self.checkLatestPackageFinished.emit(e, task.packages)
        self.message("Check Latest Python Package Finished")


class Worker(QRunnable):
    def __init__(self, obj):
        super(Worker, self).__init__()
        self.obj = obj

    def run(self):
        # noinspection PyBroadException
        try:
            self.obj.run()
        except:
            import traceback
            traceback.print_exc()


def push_task(task):
    # noinspection PyArgumentList
    thread_pool = QThreadPool.globalInstance()
    worker = Worker(task)
    thread_pool.start(worker)
