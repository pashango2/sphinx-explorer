# -*- mode: python -*-

block_cipher = None


a = Analysis(['sphinx-explorer.pyw'],
             pathex=['./sphinx-explorer'],
             binaries=[],
             datas=[
                ("./css/*", "css"),
                ("./i18n/*", "i18n"),
                ("./icon/*", "icon"),
                ("./plugin/editor/*", "plugin/editor"),
                ("./plugin/extension/*", "plugin/extension"),
                ("./plugin/template/*", "plugin/template"),
                ("./plugin/theme/*", "plugin/theme"),
                ("./settings/*", "settings"),
             ],
             hiddenimports=["qtpy.*", "pyqt5.*", "toml.*"],
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
          console=False,
          icon='sphinx.ico'
)

coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               name='sphinx-explorer')
