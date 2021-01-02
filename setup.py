import sys
import cx_Freeze

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
            "include_files": [
                'src/application.py',
                'src/bundles.py',
                'src/command_palette.py',
                'src/device_controls.py',
                'src/device_manager.py',
                'src/main.py',
                'src/main_window.py',
                'src/style.py',
                'src/serial_monitor.py',
                "src/devices",
                "src/log_monitor",
                "src/networking",
                "src/plugins/apps",
                "src/plugins/devices",
                "src/plugins/widgets",
                "src/qt",
            ],
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
