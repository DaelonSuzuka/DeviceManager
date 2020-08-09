from qt import *


class SigBundle(QObject):
    def __init__(self, signals, link_to=None, link=None):
        # signals need to be class attributes BEFORE QObject.__init__()
        for name, args in signals.items():
            setattr(self.__class__, name, Signal(*args))

        super().__init__()
        self.signals = signals
        self.names = list(signals.keys())

        if link_to:
            self.link_to(link_to)

        if link:
            self.link(link)
    
    def _link(self, slot, sig=None):
        """ Connect the given slot to a matching signal, if it exists """
        signal = sig if sig else slot.__name__
        if hasattr(self, signal):
            getattr(self, signal).connect(slot)

    def _link_to(self, obj):
        for name in self.names:
            if hasattr(obj, name):
                self._link(getattr(obj, name))

    def link_to(self, *args):
        """ Connect all of our signals to matching slots on the provided object, if they exist """
        for arg in args:
            if isinstance(arg, list):
                for obj in arg:
                    self._link_to(obj)
            else:
                self._link_to(arg)

        return self

    def _link_tuple(self, tup):
        signal = tup[0]
        if isinstance(tup[1], (list, tuple)):
            for func in tup[1]:
                self._link(func, sig=signal)
        else:
            self._link(tup[1], sig=signal)

    def link(self, *args):
        """ Connect the given slots to matching signals, if they exist """
        if isinstance(args[0], str):
            for arg in args[1:]:
                self._link_tuple((args[0], arg))
        else:
            for arg in args:
                if isinstance(arg, list):
                    for item in arg:
                        if isinstance(item, tuple):
                            self._link_tuple(item)
                        else:
                            self._link(item)

                elif isinstance(arg, tuple):
                    self._link_tuple(arg)

                elif isinstance(arg, dict):
                    for signal, func in arg.items():
                        self._link(func, sig=signal)

                else:
                    self._link(arg)
            
        return self


class SlotBundle(QObject):
    def __init__(self, slots, link_to=None, link=None, sig_fmt='on_{}'):
        super().__init__()
        self.slots = slots
        self.names = list(slots.keys())
        self.sig_fmt = sig_fmt

        # add signals
        signals = {self.sig_fmt.format(name):args for name, args in slots.items()}
        self._signals = SigBundle(signals)

        # add slot methods
        for name, args in slots.items():
            self._add_slot(name, args)

        if link_to:
            self.link_to(link_to)

        if link:
            self.link(link)

    def _add_slot(self, name, args):
        """ add a qt Slot to this object """
        @Slot(*args)
        def fn(self, *args):
            getattr(self._signals, f'on_{name}').emit(*args)

        setattr(self, name, fn.__get__(self, super()))

    def _link(self, func, sig=None):
        """ Connect the given function to a matching signal, if it exists """
        signal = sig if sig else func.__name__
        if hasattr(self._signals, signal):
            getattr(self._signals, signal).connect(func)

    def _link_to(self, obj):
        for name in self._signals.names:
            if hasattr(obj, name):
                self._link(getattr(obj, name))

    def link_to(self, *args):
        """ Connect all of our signals to matching functions on the provided object, if they exist """
        for arg in args:
            if isinstance(arg, list):
                for obj in arg:
                    self._link_to(obj)
            else:
                self._link_to(arg)

        return self

    def _link_tuple(self, tup):
        signal = self.sig_fmt.format(tup[0])
        if isinstance(tup[1], (list, tuple)):
            for func in tup[1]:
                self._link(func, sig=signal)
        else:
            self._link(tup[1], sig=signal)

    def link(self, *args):
        """ Connect the given functions to matching signals, if they exist """
        if isinstance(args[0], str):
            for arg in args[1:]:
                self._link_tuple((args[0], arg))
        else:
            for arg in args:
                if isinstance(arg, list):
                    for item in arg:
                        if isinstance(item, tuple):
                            self._link_tuple(item)
                        else:
                            self._link(item)

                elif isinstance(arg, tuple):
                    self._link_tuple(arg)

                elif isinstance(arg, dict):
                    for s, f in arg.items():
                        self._link_tuple((s, f)) 

                else:
                    self._link(arg)
            
        return self
