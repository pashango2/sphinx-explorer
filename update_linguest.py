import subprocess
import os
import fnmatch

ts_file = "sphinx_explorer/settings/i18n/sphinx_explorer_ja.ts"
sources = [
    "sphinx-explorer.pyw",
]

for root, dirs, files in os.walk("sphinx_explorer"):
    for file_path in fnmatch.filter(files, "*.py"):
        sources.append(os.path.join(root, file_path))

cmd = [
    "pylupdate5",
] + sources + [
    "-ts",
    ts_file,
]
subprocess.call(cmd)
