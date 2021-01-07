#!/usr/bin/env python3

from qt import *
import signal
from application import Application
import log_monitor
import appdirs
from pathlib import Path


def run():
    # configure logging
    database_path = appdirs.user_log_dir("Device Manager", "LDG Electronics")
    Path(database_path).mkdir(parents=True, exist_ok=True)
    log_monitor.install(database_path + '/log.db')
    
    # Create the Qt Application
    app = Application()

    def ctrlc_handler(sig, frame):
        app.window.close()
        app.shutdown()

    # grab the keyboard interrupt signal 
    signal.signal(signal.SIGINT, ctrlc_handler)

    # Run the main Qt loop
    app.exec_()

if __name__ == "__main__":
    run()