from qt import *
from .constants import *
import pyqtgraph as pg
import numpy as np


class DataSelector(QWidget):
    selectionChanged = Signal()

    def __init__(self, name='', parent=None):
        super().__init__(parent=parent)
        self.name = name

        changed = self.selectionChanged
        
        self.on = PersistentCheckBox(f'{name}_on', changed=changed)
        self.points = PersistentCheckBox(f'{name}_points', changed=changed)
        self.line = PersistentCheckBox(f'{name}_line', changed=changed)
        self.freqs = PersistentListWidget(f'{name}_freqs', items=['none']+freqs, default=['none'], selectionMode=QAbstractItemView.ExtendedSelection, changed=changed)
        field_names = [data_field_names[f] for f in data_fields]
        self.x = PersistentComboBox(f'{name}_x', items=field_names, changed=changed)
        self.y = PersistentComboBox(f'{name}_y', items=field_names, changed=changed)

        with CVBoxLayout(self) as vbox:
            with CHBoxLayout(vbox) as hbox:
                hbox.add(QLabel(name))
                hbox.add(QLabel(), 1)
                hbox.add(QLabel('Pts:'))
                hbox.add(self.points)
                hbox.add(QLabel('Line:'))
                hbox.add(self.line)
                hbox.add(QLabel('On:'))
                hbox.add(self.on)
            with CHBoxLayout(vbox) as hbox:
                hbox.add(QLabel('X:'))
                hbox.add(self.x, 1)
            with CHBoxLayout(vbox) as hbox:
                hbox.add(QLabel('Y:'))
                hbox.add(self.y, 1)

    def get_params(self):
        if self.on.checkState() and self.x.currentText() != self.y.currentText():
            return {
                'x': data_field_names.inverse[self.x.currentText()][0], 
                'y': data_field_names.inverse[self.y.currentText()][0], 
                'on': self.on.checkState(), 
                'points': self.points.checkState(), 
                'line': self.line.checkState(), 
                'freqs': self.freqs.selected_items(),
            }
        return


class GraphTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        
        self.plot_layout = pg.GraphicsLayoutWidget()
        self.custom_plots = [DataSelector(f'Custom Plot {i}', self) for i in range(1, 5)]

        def normalize(x):
            x = np.asarray(x)
            return (x - x.min()) / (np.ptp(x))

        self.freq_colors = dict(zip(freqs, normalize([float(f) for f in freqs])))

        self.freqs = PersistentListWidget(
            'graph_freqs', items=freqs, selectionMode=QAbstractItemView.ExtendedSelection, changed=self.draw_plots)
        self.freq_tabs = PersistentTabWidget('graph_tabs')
        self.freq_tabs.addTab(self.freqs, 'all')
        for plot in self.custom_plots:
            self.freq_tabs.addTab(plot.freqs, plot.name[11:])
        self.freq_tabs.restore_state()

        self.fwd_v = PersistentCheckBox('graph_fwd_v', changed=self.draw_plots)
        self.fwd_w = PersistentCheckBox('graph_fwd_w', changed=self.draw_plots)

        with CHBoxLayout(self) as layout:
            with CVBoxLayout(layout) as vbox:
                vbox.add(QLabel('Reference Plots:'))
                with CHBoxLayout(vbox) as hbox:
                    hbox.add(QLabel('Forward Volts:'))
                    hbox.add(self.fwd_v)
                with CHBoxLayout(vbox) as hbox:
                    hbox.add(QLabel('Forward Watts:'))
                    hbox.add(self.fwd_w)
                vbox.add(HLine())
                vbox.add(QLabel('Custom Plot Freqs:'))
                vbox.add(self.freq_tabs, 1)
                vbox.add(self.custom_plots)
            layout.add(self.plot_layout, 1)

        self.data = {}

        for plot in self.custom_plots:
            plot.selectionChanged.connect(self.draw_plots)

    def get_color_map(self, freqs):
        x = np.asarray([float(f) for f in freqs])
        lower = x.min()
        upper = x.max()
        normals = (x - lower) / (upper - lower)

        return dict(zip(freqs, normals))

    def poly_to_points(self, x1, poly):
        x2 = range(int(max(x1)))
        y2 = [poly(p) for p in x2]
        return x2, y2

    def add_forward_volts_plot(self):
        title = 'Forward Volts'
        labels = {'bottom':'Meter: Forward Watts', 'left':'Target: Forward Volts'}
        plot = self.plot_layout.addPlot(title=title, labels=labels)
        self.plot_added()
        plot.showGrid(x=True, y=True)
        plot.showButtons()
        plot.addLegend()

        colors = self.get_color_map(freqs)
        for freq in freqs:
            points = [p for p in self.data if p['freq'] == freq]
            x = [p['m_fwd'] for p in points]
            y = [p['t_fwd_volts'] for p in points]

            poly = np.poly1d(np.polyfit(x, y, 2))
            x2, y2 = self.poly_to_points(x, poly)

            plot.plot(x2, y2, pen=pg.hsvColor(colors[freq]), name=freq)
            plot.plot(x, y, pen=None, symbol='o', symbolSize=3, symbolPen=pg.hsvColor(colors[freq]))

    def add_forward_watts_plot(self):
        title = 'Forward Watts with Reference Line'
        labels = {'bottom':'Meter: Forward Watts', 'left':'Target: Forward Watts'}
        plot = self.plot_layout.addPlot(title=title, labels=labels)
        self.plot_added()
        plot.showGrid(x=True, y=True)
        plot.showButtons()
        plot.addLegend()

        reference_points = list(range(0, 210, 10))
        plot.plot(reference_points, reference_points, pen='w')
        
        colors = self.get_color_map(freqs)
        for freq in freqs:
            points = [p for p in self.data if p['freq'] == freq]
            x = [p['m_fwd'] for p in points]
            y = [p['t_fwd_watts'] for p in points]

            poly = np.poly1d(np.polyfit(x, y, 2))
            x2, y2 = self.poly_to_points(x, poly)

            plot.plot(x2, y2, pen=pg.hsvColor(colors[freq]), name=freq)
            plot.plot(x, y, pen=None, symbol='o', symbolSize=3, symbolPen=pg.hsvColor(colors[freq]))

    def add_custom_plot(self, params):
        title = 'Custom Plot'
        labels = {'bottom':data_field_names[params['x']], 'left':data_field_names[params['y']]}
        plot = self.plot_layout.addPlot(title=title, labels=labels)
        plot.showGrid(x=True, y=True)
        plot.showButtons()
        plot.addLegend()

        self.plot_added()

        plot_freqs = params['freqs']
        if 'none' in params['freqs']:
            plot_freqs = freqs
        colors = self.get_color_map(plot_freqs)

        for freq in plot_freqs:
            points = [p for p in self.data if p['freq'] == freq]
            x = [p[params['x']] for p in points]
            y = [p[params['y']] for p in points]

            name = freq
            if params['line']:
                poly = np.poly1d(np.polyfit(x, y, 2))
                x2, y2 = self.poly_to_points(x, poly)

                plot.plot(x2, y2, pen=pg.hsvColor(colors[freq]), name=name)
                name = None
            if params['points']:
                plot.plot(x, y, pen=None, symbol='o', symbolSize=3, symbolPen=pg.hsvColor(colors[freq]), name=name)
                name = None

    def reset_plot(self):
        self.plot_layout.clear()
        self.number_of_plots = 0

    def plot_added(self):
        self.number_of_plots += 1
        if self.number_of_plots % 2 == 0:
            self.plot_layout.nextRow()

    def draw_plots(self):
        freqs = self.freqs.selected_items()
        plot_params = [plot.get_params() for plot in self.custom_plots]
        self.reset_plot()
        
        if self.fwd_v.isChecked():
            self.add_forward_volts_plot()
        if self.fwd_w.isChecked():
            self.add_forward_watts_plot()

        for params in plot_params:
            if params is None:
                continue

            self.add_custom_plot(params)

    def set_data(self, data):
        self.data = data
        self.draw_plots()