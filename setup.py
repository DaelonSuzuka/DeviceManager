import sys
import cx_Freeze

base = None
if (sys.platform == "win32"):
    base = "Win32GUI" 


exe = [
    cx_Freeze.Executable(
        "src/main.py", 
        targetName='BenchControl', 
        base=base,
        shortcutName='BenchControl',
        shortcutDir='DesktopFolder'
        )
]

cx_Freeze.setup(
    name = "BenchControl",
    version = "1.0",
    options =  {
        "build_exe":{
            "packages": [
                'serial',
                'pyte',
            ],
            'excludes': [
                'tkinter'
            ],
            "include_files": [
                'src/bundles.py',
                'src/command_palette.py',
                'src/device_controls.py',
                'src/device_manager.py',
                'src/device_widgets.py',
                'src/diagnostics.py',
                'src/log_monitor.py',
                'src/main.py',
                'src/main_window.py',
                'src/manual_tuner.py ',
                'src/remote_devices.py',
                'src/serial_monitor.py',
                'src/servitor.py',
                'src/slickpicker.py',
                'src/style.py',
                'src/thread.py',
                'src/tuner.py',
                "src/devices",
                "src/qt",
            ]
        }
    },
    executables = exe
) 
