#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division, print_function, absolute_import, unicode_literals
from qtpy.QtCore import *
# from qtpy.QtGui import *
# from qtpy.QtWidgets import *
from ..util.python_venv import search_anaconda, search_venv, PythonVEnv
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
    finished = Signal(PythonVEnv)

    def __init__(self, settings, parent=None):
        # type: () -> None
        super(SystemInitTask, self).__init__(parent)
        self.settings = settings

    def run(self):
        self.message("Checking Anaconda...")
        conda_env = search_anaconda()

        self.message("Checking System Python...")
        venv_list = []
        for path in self.settings.search_venv_path_list():
            venv_list.extend(search_venv(path, fullpath=True))

        env = PythonVEnv(conda_env, venv_list)
        self.message("Check Version")
        env.check_version()

        self.message("System Check Finished")

        self.finished.emit(env)


class Worker(QRunnable):
    def __init__(self, obj):
        super(Worker, self).__init__()
        self.obj = obj

    def run(self):
        try:
            self.obj.run()
        except:
            import traceback

            traceback.print_exc()
            print("kita0")
            pass


def push_task(task):
    # noinspection PyArgumentList
    thread_pool = QThreadPool.globalInstance()
    worker = Worker(task)
    thread_pool.start(worker)
