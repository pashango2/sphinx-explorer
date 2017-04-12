import subprocess
import os
import zipfile
import platform
import sys
from sphinx_explorer import __version__

cmd = [
    "pyinstaller",
    "--onefile",
    "--noconsole",
    "--icon=sphinx.ico",
    "sphinx-explorer.pyw"
]
result = subprocess.call(cmd)

include_dirs = [
    "plugin", "script", "settings", "icon", "i18n"
]

if result == 0:
    def zipdir(path, ziph):
        # ziph is zipfile handle
        for root, dirs, files in os.walk(path):
            for file_path in files:
                ziph.write(os.path.join(root, file_path))

    if platform.system() == "Windows":
        ext = ".exe"
        platform_name = "win"
    elif platform.system() == "Darwin":
        ext = ""
        platform_name = "mac"
    elif platform.system() == "Linux":
        ext = ""
        platform_name = "linux"
    else:
        raise ValueError()

    bits = "64" if sys.maxsize > 2 ** 32 else "32"

    exe_path = os.path.join("dist", "sphinx-explorer" + ext)
    zip_name = "sphinx-explorer_{}{}_{}.zip".format(platform_name, bits, __version__)

    with zipfile.ZipFile(zip_name, "w") as zip_file:
        zip_file.write(exe_path, "sphinx-explorer" + ext)

        for dir_name in include_dirs:
            if os.path.isdir(dir_name):
                zipdir(dir_name, zip_file)
            else:
                zip_file.write(dir_name, dir_name)




