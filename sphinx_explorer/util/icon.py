#! coding:utf-8
from qtpy.QtGui import *
import os
import six
from ..define import get_sys_path

ICON_DIR = "icon"


def load(icon_name):
    # type: (six.string_types) -> QIcon
    file_path = os.path.join(get_sys_path(), ICON_DIR, icon_name + ".png")
    icon = QIcon(file_path)
    return icon


def loading_icon():
    # type: () -> QMovie
    file_path = os.path.join(get_sys_path(), ICON_DIR, "spiffygif_16x16.gif")
    return QMovie(file_path)
