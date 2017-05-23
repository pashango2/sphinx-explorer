#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division, print_function, absolute_import, unicode_literals
from qtpy.QtWidgets import *
from qtpy.QtGui import *
from qtpy.QtCore import *


class TypeBase(object):
    is_persistent_editor = False

    def __init__(self, item, setting):
        self.item = item
        self.setting = setting

    @property
    def index(self):
        return self.item.index()

    def enum(self):
        for v in self.setting["enum"]:
            if isinstance(v, dict):
                yield v
            else:
                yield {
                    "value": v,
                    "description": str(v),
                }

    def validate(self, value):
        if "enum" in self.setting:
            for i, v in enumerate(self.enum()):
                if v.get("value") == value:
                    return value
                if v.get("description") == value:
                    return v.get("value")
            return None
        return value

    def display_value(self, value):
        if "enum" in self.setting:
            for i, v in enumerate(self.enum()):
                if v.get("value") == value:
                    return v.get("description", value)
        return value

    def control(self, parent):
        value = self.item.value

        if "enum" in self.setting:
            control = QComboBox(parent)

            select_index = -1
            for i, v in enumerate(self.enum()):
                control.addItem(
                    str(v.get("description", v.get("value"))),
                    v.get("value")
                )
                if v.get("value") == value:
                    select_index = i

            control.setCurrentIndex(select_index)
            return control

        return None


class TypeInteger(TypeBase):
    def control(self, parent):
        control = super(TypeInteger, self).control(parent)
        if control is None:
            control = QSpinBox(parent)
            control.setValue(self.item.value)

        return control


class TypeBool(TypeBase):
    is_persistent_editor = True

    def control(self, parent):
        control = QCheckBox(parent)
        control.setChecked(self.item.value)
        control.setProperty("item", self.item)

        model = self.item.model()
        if model:
            control.toggled.connect(model.setChecked)

        return control

    def display_value(self, value):
        return ""


class TypeString(TypeBase):
    def control(self, parent):
        control = super(TypeString, self).control(parent)
        if control is None:
            control = QLineEdit(parent)
            control.setText(self.item.value)

        return control

    @staticmethod
    def get_control_value(control):
        if isinstance(control, QComboBox):
            return control.currentData()
        else:
            return control.text()


