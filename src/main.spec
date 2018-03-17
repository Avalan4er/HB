# -*- mode: python -*-
# how to build exe:
# * open anaconda prompt
# * actvate environment (activate hb)
# * install pyinstaller if not installed (pip install pyinstaller)
# * cd to src folder
# * execute command: pyinstaller -F main.spec


import os

block_cipher = None

#  PROJECT_PATH = os.path.dirname(os.path.realpath(os.__file__))
PROJECT_PATH = os.getcwd()

a = Analysis([
                'main.py',
                'bot\\hots.py',
                'bot\\state_machine.py',
                'configuration\\config.py',
                'configuration\\config_objects.py',
                'configuration\\constants.py',
                'framework\\framework_objects.py',
                'framework\\match_result_helpers.py',
                'framework\\vision_helpers.py',
                'framework\\windows_helpers.py',
                'framework\\logger.py',
            ],
             pathex=[
                 PROJECT_PATH,
                 os.path.join(PROJECT_PATH, 'bot'),
                 os.path.join(PROJECT_PATH, 'configuration'),
                 os.path.join(PROJECT_PATH, 'framework'),
             ],
             binaries=[],
             datas=[
                ( os.path.join(PROJECT_PATH, 'resources\\img\\*.png'), 'resources\\img'),
                ( os.path.join(PROJECT_PATH, 'resources\\img\\loading_screen\\*.png'), 'resources\\img\\loading_screen')
             ],
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
          name='HOTS Bot',
          debug=False,
          strip=False,
          upx=True,
          runtime_tmpdir=None,
          console=True,
          icon='resources\\img\\icon.ico')
