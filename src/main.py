#!/usr/bin/env python3

from qt import *
import signal
from application import Application
import log_monitor


def run():
    # configure logging
    log_monitor.install('log.db')
    
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