import json

import numpy as np
from qtstrap import *
from qtstrap import CVBoxLayout, QLabel, QPushButton, QTextEdit, QWidget, set_font_options


class ResultsTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)

        self.everything = set_font_options(QTextEdit(''), {'setFamily': 'Courier New'})
        self.data = set_font_options(QTextEdit(''), {'setFamily': 'Courier New'})
        self.metadata = set_font_options(QTextEdit(''), {'setFamily': 'Courier New'})
        self.header = set_font_options(QTextEdit(''), {'setFamily': 'Courier New'})

        self.save = QPushButton('Save')
        self.load = QPushButton('Load')
        # self.save.clicked.connect(self.start_worker)
        self.load.clicked.connect(self.load_data)

        with CVBoxLayout(self) as layout:
            with layout.hbox():
                layout.add(QLabel(), 1)
                layout.add(self.save)
                layout.add(self.load)
            with layout.hbox():
                layout.add(self.metadata)
                layout.add(self.everything)
            with layout.hbox():
                layout.add(self.data)
                layout.add(self.header)

    def load_data(self):
        with open('calibration.json', 'r') as f:
            results = json.load(f)

        self.display_results(results)

    def display_results(self, results):
        self.everything.setText(json.dumps(results, indent=4, sort_keys=True))
        self.data.setText(json.dumps(results['data'], indent=4, sort_keys=True))

        polys = self.calculate_polys(results['data'])
        self.header.setText(self.create_poly_header(polys))

    def calculate_polys(self, results):
        freqs = {p['freq'] for p in results}
        polys = {'fwd': {}, 'rev': {}}

        for freq in freqs:
            points = [p for p in results if p['freq'] == freq]

            x = [p['t_fwd_volts'] for p in points]
            y = [p['m_fwd'] for p in points]
            temp = np.poly1d(np.polyfit(x, y, 2))

            poly = {
                'a': round(temp[2], 10),  #
                'b': round(temp[1], 10),
                'c': round(temp[0], 10),
            }

            polys['fwd'][freq] = poly

        for freq in freqs:
            points = [p for p in results if p['freq'] == freq]
            x = [p['t_rev_volts'] for p in points]
            y = [p['m_rev'] for p in points]
            temp = np.poly1d(np.polyfit(x, y, 2))
            poly = {'a': 0, 'b': 0, 'c': 0}
            poly['a'] = round(temp[2], 10)
            poly['b'] = round(temp[1], 10)
            poly['c'] = round(temp[0], 10)

            polys['rev'][freq] = poly

        return polys

    def create_poly_header(self, polys):
        header = []

        # make sure the outputs are in order
        bands = [p for p in polys['fwd']]
        bands.sort()

        header.append('polynomial_t forwardCalibrationTable[NUM_OF_BANDS] = {\r\n')
        for band in bands:
            header.append('    {' + str(polys['fwd'][band]['a']) + ', ')
            header.append(str(polys['fwd'][band]['b']) + ', ')
            header.append(str(polys['fwd'][band]['c']) + '},')
            header.append(' // ' + band + '\r\n')
        header.append('};\r\n\r\n')

        header.append('polynomial_t reverseCalibrationTable[NUM_OF_BANDS] = {\r\n')
        for band in bands:
            header.append('    {' + str(polys['rev'][band]['a']) + ', ')
            header.append(str(polys['rev'][band]['b']) + ', ')
            header.append(str(polys['rev'][band]['c']) + '},')
            header.append(' // ' + band + '\r\n')
        header.append('};\r\n\r\n')

        return ''.join(header)
