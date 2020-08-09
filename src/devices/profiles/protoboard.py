from devices import SerialDevice, DeviceWidget, CommonMessagesMixin
from qt import *


class Signals(QObject):
    @property
    def message_tree(self):
        return {}

class Protoboard(CommonMessagesMixin, SerialDevice):
    profile_name = "Protoboard"
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.signals = Signals()
        self.message_tree.merge(self.signals.message_tree)
        self.message_tree.merge(self.common_message_tree)


    @property
    def widget(self):
        w = ProtoboardWidget(self.title, self.guid)

        # connect signals


        return w


class ProtoboardWidget(DeviceWidget):
    def build_layout(self):
        layout = QVBoxLayout()

        ports = {
            'port A' : ['A0','A1','A2','A3','A4','A5','A6','A7',],
            'port B' : ['B0','B1','B2','B3','B4','B5','B6','B7',],
            'port C' : ['C0','C1','C2','C3','C4','C5','C6','C7',],
        }
        
        state_vbox = QVBoxLayout()
        for port in ports:
            label = QLabel(port)
            hbox = QHBoxLayout()
            for pin in ports[port]:
                hbox.addWidget(QLabel(f"{pin}: "))
                hbox.addWidget(QLabel(f" "))
            state_vbox.addLayout(hbox)
        state_gbox = QGroupBox("Pin State:")
        state_gbox.setLayout(state_vbox)
        layout.addWidget(state_gbox)

        output_vbox = QVBoxLayout()
        for port in ports:
            label = QLabel(port)
            hbox = QHBoxLayout()
            for pin in ports[port]:
                hbox.addWidget(QCheckBox(pin, tristate=True))
            output_vbox.addLayout(hbox)
        output_gbox = QGroupBox("Set Output:")
        output_gbox.setLayout(output_vbox)
        layout.addWidget(output_gbox)

        read_vbox = QVBoxLayout()
        for port in ports:
            label = QLabel(port)
            hbox = QHBoxLayout()
            for pin in ports[port]:
                btn = QPushButton(pin)
                hbox.addWidget(btn)
            read_vbox.addLayout(hbox)
        read_gbox = QGroupBox("Read Pin:")
        read_gbox.setLayout(read_vbox)
        layout.addWidget(read_gbox)

        self.setWidget(QWidget(layout=grid))
