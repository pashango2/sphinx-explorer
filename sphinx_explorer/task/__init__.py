#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division, print_function, absolute_import, unicode_literals
from qtpy.QtCore import *
# from qtpy.QtGui import *
# from qtpy.QtWidgets import *
from ..util.python_venv import PythonVEnv
from ..util.commander import commander
from ..pip_manager import PipListOutDateTask
import logging
logger = logging.getLogger(__name__)


class BaseTask(QObject):
    messaged = Signal(str)

    def __init__(self, parent=None):
        # type: () -> None
        super(BaseTask, self).__init__(parent)

    def message(self, msg):
        self.messaged.emit(msg)


class SystemInitTask(BaseTask):
    checkPythonEnvFinished = Signal(PythonVEnv)
    checkPythonPackageFinished = Signal(str, list)

    finished = Signal(PythonVEnv)

    def __init__(self, settings, parent=None):
        # type: () -> None
        super(SystemInitTask, self).__init__(parent)
        self.settings = settings

    def run(self):
        self.message("Checking Python Venv...")
        env = PythonVEnv.create_system_python_env(self.settings.venv_setting())

        self.message("Checking Python Venv Finished")
        self.checkPythonEnvFinished.emit(env)

        self.message("Checking Python Packages...")

        for key, e in env.env_list():
            cmd = e.activate_command()
            activate_commander = commander.create_pre_commander(cmd)

            task = PipListOutDateTask(commander=activate_commander)
            task.run()

            self.checkPythonPackageFinished.emit(e.python_path(), task.packages)

        self.message("Check Python Package Finished")


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
