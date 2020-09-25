#!/usr/bin/env python

###
# Author: Stefan Holstein
# inspired by: https://github.com/Werkov/PyQt4/blob/master/examples/widgets/analogclock.py
# Thanks to https://stackoverflow.com/
#
###

from .qt import *
import math

class AnalogGaugeWidget(QWidget):
    valueChanged = Signal(int)

    def __init__(self, parent=None):
        super(AnalogGaugeWidget, self).__init__(parent)

        self.black = QColor(0, 0, 0, 255)

        self.set_NeedleColor(50, 50, 50, 255)
        self.NeedleColorReleased = self.NeedleColor

        self.set_ScaleValueColor(50, 50, 50, 255)
        self.set_DisplayValueColor(50, 50, 50, 255)

        self.set_CenterPointColor(50, 50, 50, 255)

        self.value_needle_count = 1
        self.value_needle = QObject
        self.change_value_needle_style([QPolygon([
            QPoint(4, 4),
            QPoint(-4, 4),
            QPoint(-3, -120),
            QPoint(0, -126),
            QPoint(3, -120)
        ])])

        self.value_min = 0
        self.value_max = 1000
        self.value = self.value_min
        self.value_offset = 0
        self.value_needle_snapzone = 0.05
        self.last_value = 0

        self.gauge_color_outer_radius_factor = 1
        self.gauge_color_inner_radius_factor = 0.95
        self.debug1 = None
        self.debug2 = None
        self.scale_angle_start_value = 135
        self.scale_angle_size = 270

        self.set_scala_main_count(10)
        self.scala_subdiv_count = 5

        self.pen = QPen(QColor(0, 0, 0))
        self.font = QFont('Decorative', 20)

        self.scale_polygon_colors = []
        self.set_scale_polygon_colors([[.00, Qt.red],
                                     [.1, Qt.yellow],
                                     [.15, Qt.green],
                                     [1, Qt.transparent]])

        # initialize Scale value text
        self.set_enable_ScaleText(True)
        self.scale_fontname = "Decorative"
        self.initial_scale_fontsize = 15
        self.scale_fontsize = self.initial_scale_fontsize

        # initialize Main value text
        self.enable_value_text = True
        self.value_fontname = "Decorative"
        self.initial_value_fontsize = 40
        self.value_fontsize = self.initial_value_fontsize
        self.text_radius_factor = 0.7

        # En/disable scale / fill
        self.set_enable_barGraph(True)
        self.set_enable_filled_Polygon(True)

        self.enable_CenterPoint = True
        self.enable_fine_scaled_marker = True
        self.enable_big_scaled_marker = True

        self.needle_scale_factor = 0.8
        self.enable_Needle_Polygon = True

        self.update()

        self.rescale_method()

    def rescale_method(self):
        if self.width() <= self.height():
            self.widget_diameter = self.width()
        else:
            self.widget_diameter = self.height()

        self.change_value_needle_style([QPolygon([
            QPoint(4, 30),
            QPoint(-4, 30),
            QPoint(-2, - self.widget_diameter / 2 * self.needle_scale_factor),
            QPoint(0, - self.widget_diameter / 2 * self.needle_scale_factor - 6),
            QPoint(2, - self.widget_diameter / 2 * self.needle_scale_factor)
        ])])

        self.scale_fontsize = self.initial_scale_fontsize * self.widget_diameter / 400
        self.value_fontsize = self.initial_value_fontsize * self.widget_diameter / 400

    def change_value_needle_style(self, design):
        self.value_needle = []
        for i in design:
            self.value_needle.append(i)
        self.update()

    def update_value(self, value, mouse_controlled = False):
        if value <= self.value_min:
            self.value = self.value_min
        elif value >= self.value_max:
            self.value = self.value_max
        else:
            self.value = value
        self.valueChanged.emit(int(value))
        self.update()

    ###############################################################################################
    # Set Methods
    ###############################################################################################
    def set_NeedleColor(self, R=50, G=50, B=50, Transparency=255):
        self.NeedleColor = QColor(R, G, B, Transparency)
        self.NeedleColorReleased = self.NeedleColor

        self.update()

    def set_ScaleValueColor(self, R=50, G=50, B=50, Transparency=255):
        self.ScaleValueColor = QColor(R, G, B, Transparency)

        self.update()

    def set_DisplayValueColor(self, R=50, G=50, B=50, Transparency=255):
        self.DisplayValueColor = QColor(R, G, B, Transparency)

        self.update()

    def set_CenterPointColor(self, R=50, G=50, B=50, Transparency=255):
        self.CenterPointColor = QColor(R, G, B, Transparency)

        self.update()

    def set_enable_Needle_Polygon(self, enable = True):
        self.enable_Needle_Polygon = enable

        self.update()

    def set_enable_ScaleText(self, enable = True):
        self.enable_scale_text = enable

        self.update()

    def set_enable_barGraph(self, enable = True):
        self.enable_barGraph = enable

        self.update()

    def set_enable_value_text(self, enable = True):
        self.enable_value_text = enable

        self.update()

    def set_enable_CenterPoint(self, enable = True):
        self.enable_CenterPoint = enable

        self.update()

    def set_enable_filled_Polygon(self, enable = True):
        self.enable_filled_Polygon = enable

        self.update()

    def set_enable_big_scaled_grid(self, enable = True):
        self.enable_big_scaled_marker = enable

        self.update()

    def set_enable_fine_scaled_marker(self, enable = True):
        self.enable_fine_scaled_marker = enable

        self.update()

    def set_scala_main_count(self, count):
        if count < 1:
            count = 1
        self.scala_main_count = count

        self.update()

    def set_MinValue(self, min):
        if self.value < min:
            self.value = min
        if min >= self.value_max:
            self.value_min = self.value_max - 1
        else:
            self.value_min = min

        self.update()

    def set_MaxValue(self, max):
        if self.value > max:
            self.value = max
        if max <= self.value_min:
            self.value_max = self.value_min + 1
        else:
            self.value_max = max

        self.update()

    def set_start_scale_angle(self, value):
        self.scale_angle_start_value = value

        self.update()

    def set_total_scale_angle_size(self, value):
        self.scale_angle_size = value

        self.update()

    def set_gauge_color_outer_radius_factor(self, value):
        self.gauge_color_outer_radius_factor = float(value) / 1000

        self.update()

    def set_gauge_color_inner_radius_factor(self, value):
        self.gauge_color_inner_radius_factor = float(value) / 1000

        self.update()

    def set_scale_polygon_colors(self, color_array):
        if 'list' in str(type(color_array)):
            self.scale_polygon_colors = color_array
        elif color_array == None:
            self.scale_polygon_colors = [[.0, Qt.transparent]]
        else:
            self.scale_polygon_colors = [[.0, Qt.transparent]]

        self.update()

    ###############################################################################################
    # Get Methods
    ###############################################################################################

    def get_value_max(self):
        return self.value_max

    ###############################################################################################
    # Painter
    ###############################################################################################

    def create_polygon_pie(self, outer_radius, inner_raduis, start, lenght):
        polygon_pie = QPolygonF()
        n = 360
        w = 360 / n
        x = 0
        y = 0

        if not self.enable_barGraph:
            lenght = int(round((lenght / (self.value_max - self.value_min)) * (self.value - self.value_min)))

        for i in range(lenght+1):
            t = w * i + start
            x = outer_radius * math.cos(math.radians(t))
            y = outer_radius * math.sin(math.radians(t))
            polygon_pie.append(QPointF(x, y))
        for i in range(lenght+1):
            t = w * (lenght - i) + start
            x = inner_raduis * math.cos(math.radians(t))
            y = inner_raduis * math.sin(math.radians(t))
            polygon_pie.append(QPointF(x, y))

        polygon_pie.append(QPointF(x, y))
        return polygon_pie

    def draw_filled_polygon(self, outline_pen_with=0):
        if not self.scale_polygon_colors == None:
            painter_filled_polygon = QPainter(self)
            painter_filled_polygon.setRenderHint(QPainter.Antialiasing)
            painter_filled_polygon.translate(self.width() / 2, self.height() / 2)

            painter_filled_polygon.setPen(Qt.NoPen)

            self.pen.setWidth(outline_pen_with)
            if outline_pen_with > 0:
                painter_filled_polygon.setPen(self.pen)

            colored_scale_polygon = self.create_polygon_pie(
                ((self.widget_diameter / 2) - (self.pen.width() / 2)) * self.gauge_color_outer_radius_factor,
                (((self.widget_diameter / 2) - (self.pen.width() / 2)) * self.gauge_color_inner_radius_factor),
                self.scale_angle_start_value, self.scale_angle_size)

            gauge_rect = QRect(QPoint(0, 0), QSize(self.widget_diameter / 2 - 1, self.widget_diameter - 1))
            grad = QConicalGradient(QPointF(0, 0), - self.scale_angle_size - self.scale_angle_start_value - 1)

            for eachcolor in self.scale_polygon_colors:
                grad.setColorAt(eachcolor[0], eachcolor[1])
            painter_filled_polygon.setBrush(grad)
            painter_filled_polygon.drawPolygon(colored_scale_polygon)

    ###############################################################################################
    # Scale Marker
    ###############################################################################################

    def draw_big_scaled_markter(self):
        my_painter = QPainter(self)
        my_painter.setRenderHint(QPainter.Antialiasing)
        my_painter.translate(self.width() / 2, self.height() / 2)

        self.pen = QPen(QColor(0, 0, 0, 255))
        self.pen.setWidth(2)
        my_painter.setPen(self.pen)

        my_painter.rotate(self.scale_angle_start_value)
        steps_size = (float(self.scale_angle_size) / float(self.scala_main_count))
        scale_line_outer_start = self.widget_diameter/2
        scale_line_lenght = (self.widget_diameter / 2) - (self.widget_diameter / 20)
        for i in range(self.scala_main_count+1):
            my_painter.drawLine(scale_line_lenght, 0, scale_line_outer_start, 0)
            my_painter.rotate(steps_size)

    def create_scale_marker_values_text(self):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        painter.translate(self.width() / 2, self.height() / 2)
        font = QFont(self.scale_fontname, self.scale_fontsize)
        fm = QFontMetrics(font)

        pen_shadow = QPen()

        pen_shadow.setBrush(self.ScaleValueColor)
        painter.setPen(pen_shadow)

        text_radius_factor = 0.8
        text_radius = self.widget_diameter/2 * text_radius_factor

        scale_per_div = int((self.value_max - self.value_min) / self.scala_main_count)

        angle_distance = (float(self.scale_angle_size) / float(self.scala_main_count))
        for i in range(self.scala_main_count + 1):
            text = str(int(self.value_min + scale_per_div * i))
            w = fm.width(text) + 1
            h = fm.height()
            painter.setFont(QFont(self.scale_fontname, self.scale_fontsize))
            angle = angle_distance * i + float(self.scale_angle_start_value)
            x = text_radius * math.cos(math.radians(angle))
            y = text_radius * math.sin(math.radians(angle))
            text = [x - int(w/2), y - int(h/2), int(w), int(h), Qt.AlignCenter, text]
            painter.drawText(text[0], text[1], text[2], text[3], text[4], text[5])

    def create_fine_scaled_marker(self):
        my_painter = QPainter(self)

        my_painter.setRenderHint(QPainter.Antialiasing)
        my_painter.translate(self.width() / 2, self.height() / 2)

        my_painter.setPen(Qt.black)
        my_painter.rotate(self.scale_angle_start_value)
        steps_size = (float(self.scale_angle_size) / float(self.scala_main_count * self.scala_subdiv_count))
        scale_line_outer_start = self.widget_diameter/2
        scale_line_lenght = (self.widget_diameter / 2) - (self.widget_diameter / 40)
        for i in range((self.scala_main_count * self.scala_subdiv_count)+1):
            my_painter.drawLine(scale_line_lenght, 0, scale_line_outer_start, 0)
            my_painter.rotate(steps_size)

    def create_values_text(self):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        painter.translate(self.width() / 2, self.height() / 2)
        font = QFont(self.value_fontname, self.value_fontsize)
        fm = QFontMetrics(font)

        pen_shadow = QPen()

        pen_shadow.setBrush(self.DisplayValueColor)
        painter.setPen(pen_shadow)

        text_radius = self.widget_diameter / 2 * self.text_radius_factor

        text = str(int(self.value))
        w = fm.width(text) + 1
        h = fm.height()
        painter.setFont(QFont(self.value_fontname, self.value_fontsize))

        angle_end = float(self.scale_angle_start_value + self.scale_angle_size - 360)
        angle = (angle_end - self.scale_angle_start_value) / 2 + self.scale_angle_start_value

        x = text_radius * math.cos(math.radians(angle))
        y = text_radius * math.sin(math.radians(angle))
        text = [x - int(w/2), y - int(h/2), int(w), int(h), Qt.AlignCenter, text]
        painter.drawText(text[0], text[1], text[2], text[3], text[4], text[5])

    def draw_big_needle_center_point(self, diameter=30):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        painter.translate(self.width() / 2, self.height() / 2)
        painter.setPen(Qt.NoPen)
        painter.setBrush(self.CenterPointColor)
        painter.drawEllipse(int(-diameter / 2), int(-diameter / 2), int(diameter), int(diameter))

    def draw_needle(self):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.translate(self.width() / 2, self.height() / 2)
        painter.setPen(Qt.NoPen)
        painter.setBrush(self.NeedleColor)
        painter.rotate(((self.value - self.value_offset - self.value_min) * self.scale_angle_size /
                        (self.value_max - self.value_min)) + 90 + self.scale_angle_start_value)

        painter.drawConvexPolygon(self.value_needle[0])

    ###############################################################################################
    # Events
    ###############################################################################################

    def resizeEvent(self, event):
        self.rescale_method()

    def paintEvent(self, event):
        # colored pie area
        if self.enable_filled_Polygon:
            self.draw_filled_polygon()

        # draw scale marker lines
        if self.enable_fine_scaled_marker:
            self.create_fine_scaled_marker()
        if self.enable_big_scaled_marker:
            self.draw_big_scaled_markter()

        # draw scale marker value text
        if self.enable_scale_text:
            self.create_scale_marker_values_text()

        # Display Value
        if self.enable_value_text:
            self.create_values_text()

        # draw needle 1
        if self.enable_Needle_Polygon:
            self.draw_needle()

        # Draw Center Point
        if self.enable_CenterPoint:
            self.draw_big_needle_center_point(diameter=(self.widget_diameter / 6))