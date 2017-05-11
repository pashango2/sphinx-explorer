#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division, print_function, absolute_import, unicode_literals
import codecs
import yaml
from six import string_types

CONFIG_TYPES = {
    "boolean": {
        "type": bool,
    },
    "integer": {
        "type": int,
    },
    "string": {
        "type": str,
    },
    "array": None,
    # "color": None,
    "object": None,
    "header": None,
    "header_1": None,
    "sub_header": None,
    "header_2": None,
}

CONFIG_TYPES["number"] = CONFIG_TYPES["integer"]


class Config(object):
    def __init__(self, config):
        """
        :param dict config: config by python object(dict)
        """
        self._config = config

    @staticmethod
    def from_yaml(yaml_path, encoding="utf-8"):
        """
        load from yaml file.

        :param string_types yaml_path: yaml path
        :param string_types encoding: yaml encoding (default: utf-8)
        :rtype: Config
        """
        return Config(yaml.load(codecs.open(yaml_path, "r", encoding=encoding)))

    @staticmethod
    def from_yaml_string(yaml_string):
        """
        load from yaml file.

        :param string_types yaml_string: yaml string
        :rtype: Config
        """
        return Config(yaml.load(yaml_string))

    def get(self, key_path, *options):
        _config = self._get_from_keys(self._pars_key_path(key_path))
        if _config is None:
            raise KeyError()

        _value = _config.get("value")
        config_type = CONFIG_TYPES[_config.get("type", "string")]

        return config_type["type"](_value) if _value is not None else _config.get("default")

    def set(self, key_path, value, *options):
        _config = self._get_from_keys(self._pars_key_path(key_path))

        if _config is None:
            raise KeyError()

        if not self.has_enum(_config, value):
            raise ValueError(value)

        _config["value"] = value

    def enum(self, key_path):
        _config = self._get_from_keys(self._pars_key_path(key_path))
        return self._enum(_config) if _config else None

    @staticmethod
    def has_enum(config, value):
        if "enum" not in config:
            return True

        for x in config.get("enum"):
            if isinstance(x, dict):
                if x["value"] == value:
                    return True
            else:
                if x == value:
                    return True

        return False

    def unset(self, key_path, *options):
        pass

    def observe(self, key_path, callback, **kwargs):
        pass

    def on_did_change(self, callback, **kwargs):
        pass

    def config_iter(self):
        _config = self._config.get("config", {})

        if isinstance(_config, dict):
            for key, value in sorted(_config.items(), key=lambda x: x[1].get("order")):
                yield key, value
        elif isinstance(_config, (list, tuple)):
            for key, value in _config:
                yield key, value

    @staticmethod
    def _enum(config):
        for x in config.get("enum", []):
            if not isinstance(x, dict):
                yield x, str(x)
            else:
                yield x["value"], x["description"]

    def _get_from_keys(self, keys):
        """
        get config value from key sequence

        :param tuple keys: key sequence
        :rtype: any
        """
        _config = self._config.get("config", {})

        for key in keys:
            if key not in _config:
                raise KeyError()

            _config = _config[key]

        return _config

    @staticmethod
    def _pars_key_path(key_path):
        """
        pars key path

        :param string_types key_path: key path
        :rtype: tuple[string_types]
        """
        if isinstance(key_path, string_types):
            return tuple(key_path.split("."))
        elif isinstance(key_path, (list, tuple)):
            return tuple(key_path)
        else:
            raise ValueError(key_path)


def main():
    yaml_string = """
config:
  zSetting:
    type: 'integer'
    default: 4
    order: 1
  aSetting:
    type: 'integer'
    default: 4
    order: 2
    """.strip()

    config = Config.from_yaml_string(yaml_string)

    assert config.get("zSetting") == 4
    assert config.get("aSetting") == 4
    assert ("zSetting", "aSetting") == tuple(key for key, _ in config.config_iter())

    yaml_string = """
config:
  someSetting:
    type: 'integer'
    default: 4
    enum: [2, 4, 6, 8]
    """.strip()

    config = Config.from_yaml_string(yaml_string)

    assert config.get("someSetting") == 4
    try:
        config.set("someSetting", 0)
    except ValueError:
        pass
    else:
        assert False

    config.set("someSetting", 6)
    assert config.get("someSetting") == 6

    yaml_string = """
config:
  someSetting:
    type: 'string'
    default: 'foo'
    enum: [
      {value: 'foo', description: 'Foo mode. You want this.'},
      {value: 'bar', description: 'Bar mode. Nobody wants that!'}
    ]
    """.strip()

    config = Config.from_yaml_string(yaml_string)

    assert config.get("someSetting") == "foo"
    try:
        config.set("someSetting", "s")
    except ValueError:
        pass
    else:
        assert False

    config.set("someSetting", "bar")
    assert config.get("someSetting") == "bar"

    ans = [('foo', 'Foo mode. You want this.'), ('bar', 'Bar mode. Nobody wants that!')]
    assert ans == list(config.enum("someSetting"))


if __name__ == "__main__":
    main()

