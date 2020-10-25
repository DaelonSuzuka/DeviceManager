
freqs = ["01800000", "03500000", "07000000", "10100000", "14000000", "18068000", "21000000", "24890000", "28000000", "50000000", ]
powers = ["005", "010", "015", "020", "025", "030", "035", "040", "050", "060", "070", "080", "090", "100", "110", "120", ]
data_fields = [
    'm_fwd', 'm_rev', 'm_swr', 'm_freq', 'm_temp',
    't_fwd_volts', 't_rev_volts', 't_mq', 
    't_fwd_watts', 't_rev_watts', 't_swr', 't_freq',
]

class bidict(dict):
    def __init__(self, *args, **kwargs):
        super(bidict, self).__init__(*args, **kwargs)
        self.inverse = {}
        for key, value in self.items():
            self.inverse.setdefault(value,[]).append(key) 

    def __setitem__(self, key, value):
        if key in self:
            self.inverse[self[key]].remove(key) 
        super(bidict, self).__setitem__(key, value)
        self.inverse.setdefault(value,[]).append(key)        

    def __delitem__(self, key):
        self.inverse.setdefault(self[key],[]).remove(key)
        if self[key] in self.inverse and not self.inverse[self[key]]: 
            del self.inverse[self[key]]
        super(bidict, self).__delitem__(key)


data_field_names = bidict({
    'm_fwd': 'Meter: Forward Watts',
    'm_rev': 'Meter: Reverse Watts',
    'm_swr': 'Meter: SWR',
    'm_freq': 'Meter: Frequency',
    'm_temp': 'Meter: Temperature',
    't_fwd_volts': 'Target: Forward Volts',
    't_rev_volts': 'Target: Reverse Volts',
    't_mq': 'Target: Match Quality',
    't_fwd_watts': 'Target: Forward Watts',
    't_rev_watts': 'Target: Reverse Watts',
    't_swr': 'Target: SWR',
    't_freq': 'Target: Frequency',
})