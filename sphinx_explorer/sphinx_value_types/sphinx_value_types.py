#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division, print_function, absolute_import, unicode_literals
from sphinx_explorer.property_widget import TypeBase, TypeChoice
from .widgets import *
from sphinx_explorer.theme_dialog import HtmlThemeWidget
# from qtpy.QtCore import *
# from qtpy.QtGui import *
from qtpy.QtWidgets import *
from sphinx_explorer.util import python_venv


# noinspection PyMethodOverriding,PyArgumentList
class TypeLanguage(TypeBase):
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
    def control(cls, _, parent):
        combo = QComboBox(parent)

        for i, line in enumerate(cls.Languages.splitlines()):
            combo.addItem(line.strip())
            code = line.split("–")[0].strip()
            combo.setItemData(i, code)

        return combo

    @classmethod
    def set_value(cls, combo, value):
        # type: (QComboBox, str) -> None
        index = combo.findData(value)
        combo.setCurrentIndex(index)

    @classmethod
    def value(cls, combo):
        # type: (QComboBox, str) -> None
        return combo.itemData(combo.currentIndex())


# noinspection PyMethodOverriding
class TypeHtmlTheme(TypeBase):
    @classmethod
    def control(cls, _, parent):
        return HtmlThemeWidget(parent)

    @classmethod
    def set_value(cls, control, value):
        control.setText(value)

    @classmethod
    def value(cls, control):
        return control.text()


class TypePython(TypeChoice):
    is_persistent_editor = True

    def __init__(self, value):
        super(TypePython, self).__init__(value)

    def control(self, delegate, parent):
        ctrl = PythonComboButton(parent)
        self.setup_combo_box(ctrl.combo_box)
        return ctrl

    @classmethod
    def create(cls, params):
        combo = TypePython(params)

        project_path = params.get("project_path")
        extend_venv = []
        if project_path:
            extend_venv += python_venv.search_venv(project_path, fullpath=True)

        choices = []
        env_list, default_value = python_venv.sys_env.env_list(venv_list=extend_venv)
        for key, env in env_list:
            choices.append({
                "text": str(env),
                "value": key,
                "icon": python_venv.ICON_DICT[env.type],
            })

        if params.get("is_project", False):
            choices.append({
                "text": "Use Sphinx Explorer Default",
                "value": None,
                "icon": python_venv.ICON_DICT["sys"],
            })
        combo.setup_choices(choices)

        return combo

    def sizeHint(self):
        return PythonComboButton().sizeHint()