#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division, print_function, absolute_import, unicode_literals
from qtpy.QtCore import *
# from qtpy.QtGui import *
# from qtpy.QtWidgets import *
from ..util.python_venv import anaconda_env, python_venv, PythonVEnv


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
        conda_env = anaconda_env()

        self.message("Checking System Python...")
        venv_list = []
        for path in self.settings.search_venv_path_list():
            venv_list.extend(python_venv(path, fullpath=True))

        self.message("System Check Finished")

        env = PythonVEnv(conda_env, venv_list)
        self.finished.emit(env)


class Worker(QRunnable):
    def __init__(self, obj):
        super(Worker, self).__init__()
        self.obj = obj

    def run(self):
        self.obj.run()


def push_task(task):
    # noinspection PyArgumentList
    thread_pool = QThreadPool.globalInstance()
    worker = Worker(task)
    thread_pool.start(worker)
