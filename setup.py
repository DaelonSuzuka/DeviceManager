import sys
import cx_Freeze
from pathlib import Path


base = None
if (sys.platform == "win32"):
    base = "Win32GUI" 


cx_Freeze.setup(
    name = "BenchControl",
    version = "1.0",
    options =  {
        "build_exe":{
            "packages": [
                'serial',
                'pyte',
                'pyside2',
                'qtawesome',
                'qtpy',
                'pyqtgraph',
                'numpy',
                'wcwidth',
                'shiboken2',
            ],
            'excludes': [
                'tkinter'
            ],
            "include_files": [f.as_posix() for f in Path('src').rglob('*.py')],
            "includes": [
                "dataclasses",
            ]
        }
    },
    executables = [
        cx_Freeze.Executable(
            "src/main.py", 
            targetName='BenchControl', 
            base=base,
            shortcutName='BenchControl',
            shortcutDir='DesktopFolder'
            )
    ]
) 
