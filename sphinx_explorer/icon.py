#! coding:utf-8
from PySide.QtGui import *
import os

ICON_DIR = "icon"


def load(icon_name):
    # type: (str) -> QIcon
    file_path = os.path.join(ICON_DIR, icon_name + ".png")
    icon = QIcon(os.path.join(os.getcwd(), file_path))
    return icon
