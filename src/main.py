#!/usr/bin/env python3

from qtstrap import *
from qtstrap.extras import log_monitor
from application import Application
import appdirs
from pathlib import Path


def run():
    log_monitor.install()
    
    # Create the Qt Application
    app = Application()

    # Run the main Qt loop
    app.exec_()

if __name__ == "__main__":
    run()