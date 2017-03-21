#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division, print_function, absolute_import, unicode_literals
from PySide.QtGui import *
from PySide.QtCore import *
import os

# from sphinx import quickstart
# from sphinx.quickstart import ask_user, generate, do_prompt, nonempty, boolean
#
#
# def queistions(path):
#     # type: (str) -> dict
#     d = {'path': path}
#
#     # begin monkey patch
#     quickstart.do_prompt = _do_prompt
#
#     quickstart.ask_user(d)
#
#     # end monkey patch
#     quickstart.do_prompt = do_prompt
#
#     return d
#
#
# # def do_prompt(d, key, text, default=None, validator=nonempty):
# def _do_prompt(d, key, text, default=None, validator=nonempty):
#     print(d, key, text)
#     pass


from .quickstart_dialog_ui import Ui_Dialog


class Param(object):
    def __init__(self, key, text, param_type, default=None, validator=None):
        self.key = key
        self.text = text
        self.param_type = param_type
        self.default = default
        self.validator = validator

    def control(self, parent):
        return self.param_type.control(self.default, parent)


class ParamType(object):
    @classmethod
    def control(cls, default, parent):
        pass


class PathParamWidget(QWidget):
    def __init__(self, parent=None):
        super(PathParamWidget, self).__init__(parent)
        self.line_edit = QLineEdit(self)
        self.ref_button = QToolButton(self)
        self.ref_button.setText("...")
        self.ref_button.setAutoRaise(True)
        # self.ref_button.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        self.ref_button.setContentsMargins(0, 0, 0, 0)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.line_edit)
        layout.addWidget(self.ref_button)

        # noinspection PyUnresolvedReferences
        self.ref_button.clicked.connect(self.onRefButtonClicked)

    def onRefButtonClicked(self):
        cwd = self.line_edit.text() or os.getcwd()

        # noinspection PyCallByClass
        path_dir = QFileDialog.getExistingDirectory(
            self, "Sphinx root path", cwd
        )
        if path_dir:
            self.line_edit.setText(path_dir)

    def setText(self, text):
        self.line_edit.setText(text)


class PathParamType(ParamType):
    @classmethod
    def control(cls, default, parent):
        widget = PathParamWidget(parent)
        widget.setText(default)
        return widget


class BoolParamType(ParamType):
    @classmethod
    def control(cls, default, parent):
        widget = QCheckBox(parent)
        if default is not None:
            widget.setChecked(default)
        return widget


class LineParamType(ParamType):
    @classmethod
    def control(cls, default, parent):
        widget = QLineEdit(parent)
        widget.setText(default)
        return widget


class LanguageParamType(ParamType):
    Languages = """
    bn – ベンガル語
    ca – カタロニア語
    cs – チェコ語
    da – デンマーク語
    de – ドイツ語
    en – 英語
    es – スペイン語
    et – エストニア語
    eu – バスク語
    fa – イラン語
    fi – フィンランド語
    fr – フランス語
    he – ヘブライ語
    hr – クロアチア語
    hu – ハンガリー語
    id – インドネシア
    it – イタリア語
    ja – 日本語
    ko – 韓国語
    lt – リトアニア語
    lv – ラトビア語
    mk – マケドニア
    nb_NO – ノルウェー語
    ne – ネパール語
    nl – オランダ語
    pl – ポーランド語
    pt_BR – ブラジルのポーランド語
    pt_PT – ヨーロッパのポルトガル語
    ru – ロシア語
    si – シンハラ
    sk – スロバキア語
    sl – スロベニア語
    sv – スウェーデン語
    tr – トルコ語
    uk_UA – ウクライナ語
    vi – ベトナム語
    zh_CN – 簡体字中国語
    zh_TW – 繁体字中国語
    """.strip()

    @classmethod
    def control(cls, default, parent):
        combo = QComboBox(parent)

        for i, line in enumerate(cls.Languages.splitlines()):
            combo.addItem(line.strip())

            code = line.split("–")[0].strip()
            if code == default:
                combo.setCurrentIndex(i)

        return combo


class QuickStartDialog(QDialog):
    Params = [
        Param("path", "root path", PathParamType, os.getcwd()),
        Param("sep", "separate source and build dirs", BoolParamType, True),
        Param("dot", "replacement for dot in _templates etc.", LineParamType),
        Param("project", "project name", LineParamType),
        Param("author", "author names", LineParamType),
        Param("version", "version of project", LineParamType),
        Param("release", "release of project", LineParamType),
        Param("language", "document language", LanguageParamType, "ja"),
        Param("suffix", "source file suffix", LineParamType),
        Param("master", "master document name", LineParamType),
        Param("epub", "use epub", BoolParamType, False),
        Param("makefile", "make Makefile", BoolParamType, True),
        Param("batchfile", "make command file", BoolParamType, True),
    ]

    def __init__(self, parent=None):
        """
        :type parent: QWidget
        """
        super(QuickStartDialog, self).__init__(parent)
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)

        for param in self.Params:
            self.ui.from_layout.addRow(
                param.text,
                param.control(self)
            )
