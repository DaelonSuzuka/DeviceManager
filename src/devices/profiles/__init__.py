#!/usr/bin/env python3

# This is a wierd hack but I don't care.

# I need to look up subclasses of SerialDevice to resolve the correct device
# profile when a device connects. In order for SerialDevice.__subclasses__() to
# get populated, all the subclasses need to be imported too.

# Since I don't feel like maintaining a list of all the classes to import, I'm
# left with this gross blob of shit that I found here:
# https://julienharbulot.com/python-dynamical-import.html


# import os, sys
# from pathlib import Path

# dir_path = os.path.dirname(os.path.abspath(__file__))
# files = [str(f.relative_to(dir_path).as_posix())[:-3] for f in Path(dir_path).rglob("*.py")]
# if '__init__' in files:
#     files.remove('__init__')

# files = [f.replace('/', '.') for f in files]

# [print(f) for f in files]

# for f in files:
#     mod = __import__('.'.join([__name__, f]), fromlist=[f])
#     to_import = [getattr(mod, x) for x in dir(mod) if isinstance(getattr(mod, x), type)]

#     for i in to_import:
#         try:
#             setattr(sys.modules[__name__], i.__name__, i)
#         except AttributeError:
#             pass


from .alpha4510A import Alpha4510A
from .at600proII import AT600ProII
from .dts4 import DTS4
from .kenwoodTS480 import TS480
from .protoboard import Protoboard
from .rf_sensor import RFSensor
from .sw100 import SW100
from .sw4u import SW4U
from .unknown_device import UnknownDevice
from .variablecapacitor import VariableCapacitor
from .variableinductor import VariableInductor
from .variable_dummy_load import VariableDummyLoad
from .yaesuFT991 import FT991
from .console_device import ConsoleDevice
from .radio_interface import RadioInterface
from .judi_pedals import JudiPedals