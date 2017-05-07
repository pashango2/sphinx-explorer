# -*- mode: python -*-

block_cipher = None


a = Analysis(['sphinx-explorer.pyw'],
             pathex=['C:\\Users\\056-kusakabe-n\\AppData\\Local\\Programs\\Python\\Python35\\Lib\\site-packages\\PyQt5\\Qt\\bin', 'C:\\Users\\056-kusakabe-n\\Documents\\sphinx-explorer'],
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
          exclude_binaries=True,
          name='sphinx-explorer',
          debug=False,
          strip=False,
          upx=True,
          console=True , icon='sphinx.ico')
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               name='sphinx-explorer')
