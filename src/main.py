#!/usr/bin/env python3

from qt import *
import signal
from application import Application
import logging
from log_monitor import log_handler


def run():
    # configure logging
    logging.basicConfig(filename='log.txt', level=logging.DEBUG)
    # add loghandler to redirect logs into the LogMonitor widget
    logging.getLogger().addHandler(log_handler)

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