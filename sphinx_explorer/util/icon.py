#! coding:utf-8
from qtpy.QtGui import *
import os
import six

ICON_DIR = "icon"


def load(icon_name):
    # type: (six.string_types) -> QIcon
    file_path = os.path.join(ICON_DIR, icon_name + ".png")
    icon = QIcon(os.path.join(os.getcwd(), file_path))
    return icon


def loading_icon():
    # type: () -> QMovie
    file_path = os.path.join(ICON_DIR, "spiffygif_16x16.gif")
    return QMovie(file_path)
