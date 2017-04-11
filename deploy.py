import subprocess
import os
import zipfile
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
    "plugin", "script", "settings", "icon"
]

if result == 0:
    def zipdir(path, ziph):
        # ziph is zipfile handle
        for root, dirs, files in os.walk(path):
            for file_path in files:
                ziph.write(os.path.join(root, file_path))

    exe_path = os.path.join("dist", "sphinx-explorer.exe")
    zip_name = "sphinx-explorer_win_AMD64_{}.zip".format(__version__)

    with zipfile.ZipFile(zip_name, "w") as zip_file:
        zip_file.write(exe_path, "sphinx-explorer.exe")

        for dir_name in include_dirs:
            zipdir(dir_name, zip_file)




