from qt import *
from devices import DeviceManager


@DeviceManager.subscribe_to("RFSensor")
class RFSensorChartWidget(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.swr_meter = AnalogGaugeWidget()
        self.swr_meter.set_start_scale_angle(200)
        self.swr_meter.set_total_scale_angle_size(140)
        self.swr_meter.set_MinValue(0)
        self.swr_meter.set_MaxValue(4096)
        self.swr_meter.set_enable_value_text(False)
        self.swr_meter.set_NeedleColor(R=200, G=200, B=200)
        self.swr_meter.set_ScaleValueColor(R=200, G=200, B=200)
        self.swr_meter.set_CenterPointColor(R=150, G=150, B=150)

        self.phase_meter = AnalogGaugeWidget()
        self.phase_meter.set_start_scale_angle(200)
        self.phase_meter.set_total_scale_angle_size(140)
        self.phase_meter.set_MinValue(-500)
        self.phase_meter.set_MaxValue(500)
        self.phase_meter.set_enable_value_text(False)
        self.phase_meter.set_NeedleColor(R=200, G=200, B=200)
        self.phase_meter.set_ScaleValueColor(R=200, G=200, B=200)
        self.phase_meter.set_CenterPointColor(R=150, G=150, B=150)

        self.mag_meter = AnalogGaugeWidget()
        self.mag_meter.set_start_scale_angle(200)
        self.mag_meter.set_total_scale_angle_size(140)
        self.mag_meter.set_MinValue(0)
        self.mag_meter.set_MaxValue(4096)
        self.mag_meter.set_enable_value_text(False)
        self.mag_meter.set_NeedleColor(R=200, G=200, B=200)
        self.mag_meter.set_ScaleValueColor(R=200, G=200, B=200)
        self.mag_meter.set_CenterPointColor(R=150, G=150, B=150)

        with CGridLayout(self) as layout:
            layout.add(self.swr_meter, 0, 0)
            layout.add(self.phase_meter, 0, 1)
            layout.add(self.mag_meter, 0, 2)

    def connected(self, device):
        device.signals.swr.connect(lambda x: self.swr_meter.update_value(x))
        device.signals.phase.connect(lambda x: self.phase_meter.update_value(x))