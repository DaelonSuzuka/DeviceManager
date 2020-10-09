import os, sys
from pathlib import Path

dir_path = os.path.dirname(os.path.abspath(__file__))
files = [str(f.relative_to(dir_path).as_posix())[:-3] for f in Path(dir_path).rglob("*.py")]
if '__init__' in files:
    files.remove('__init__')

files = [f.replace('/', '.') for f in files]

for f in files:
    mod = __import__('.'.join([__name__, f]), fromlist=[f])
    to_import = [getattr(mod, x) for x in dir(mod) if isinstance(getattr(mod, x), type)]

    for i in to_import:
        try:
            setattr(sys.modules[__name__], i.__name__, i)
        except AttributeError:
            pass

apps = [x for x in QWidget.__subclasses__() if x.__name__.endswith('App')]

# until the main ui supports reordering tabs, lets force the servitor
# app to the front of the list
apps.insert(0, apps.pop(apps.index(ServitorApp)))