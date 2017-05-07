#! coding:utf-8
from qtpy.QtGui import *
import os
import six

ICON_DIR = "settings/icon"


def init(sys_dir):
    global ICON_DIR
    ICON_DIR = os.path.join(sys_dir, ICON_DIR)


def load(icon_name):
    # type: (six.string_types) -> QIcon
    file_path = os.path.join(ICON_DIR, icon_name + ".png")
    icon = QIcon(file_path)
    return icon


def loading_icon():
    # type: () -> QMovie
    file_path = os.path.join(ICON_DIR, "spiffygif_16x16.gif")
    return QMovie(file_path)
