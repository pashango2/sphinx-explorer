# -*- mode: python -*-
import os
import PyQt5

block_cipher = None

qt_bin_pth = os.path.join(os.path.dirname(PyQt5.__file__), 'Qt', 'bin')

a = Analysis(['sphinx-explorer.pyw'],
             pathex=[qt_bin_pth, '.'],
             binaries=[],
             datas=[],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='sphinx-explorer',
          debug=False,
          strip=False,
          upx=True,
          console=False , icon='sphinx.ico')


import shutil

try:
    shutil.rmtree(os.path.join("dist", "settings"))
except:
    pass

shutil.copytree(
    os.path.join("sphinx_explorer", "settings"),
    os.path.join("dist", "settings")
)