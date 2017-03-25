#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division, print_function, absolute_import, unicode_literals
import sys
import os
import subprocess
import json
import platform


TERM_ENCODING = getattr(sys.stdin, 'encoding', None)


def main(config_py_path):
    # type: (str) -> None
    dir_name, base_name = os.path.split(config_py_path)
    module_name = os.path.splitext(base_name)[0]

    # noinspection PyBroadException
    try:
        sys.path.append(dir_name)
        conf = __import__(module_name)
    except:
        sys.exit(1)
    finally:
        sys.path.pop()

    obj = {
        "project": conf.project,
        "author": conf.author,
        "version": conf.version,
        "extensions": conf.extensions,
        "source_suffix": conf.source_suffix,
        "html_theme": conf.html_theme,
        "language": conf.language,
    }
    print(json.dumps(obj, indent=4))


def get(config_py_path):
    # type: (str) -> dict
    cmd = " ".join(["python", __file__, config_py_path])
    result = check_output(cmd)
    result = json.loads(result.decode(TERM_ENCODING))
    return result


def check_output(cmd):
    # type: (str) -> bytes
    if platform.system() in ("Windows", "Darwin"):
        return subprocess.check_output(cmd, shell=True)
    else:
        return subprocess.check_output(['/bin/bash', '-i', '-c', cmd])


if __name__ == "__main__":
    main(sys.argv[1])
    sys.exit(0)
