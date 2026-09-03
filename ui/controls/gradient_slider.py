from PySide6.QtCore import Qt
from PySide6.QtGui import QPainter, QLinearGradient, QColor, QPen
from PySide6.QtWidgets import QStyleOptionSlider, QStyle

from ui.controls.smart_slider import SmartSlider


class GradientSlider(SmartSlider):
    """Hue slider with the same interaction model as every other slider."""

    def __init__(self, orientation, parent=None, mode="hue"):
        super().__init__(orientation, parent)
        self.mode = mode
        self.setFixedHeight(18)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)
        option = QStyleOptionSlider()
        self.initStyleOption(option)

        groove_h = 8
        groove_y = (self.height() - groove_h) // 2
        left = 2
        right = self.width() - 2

        gradient = QLinearGradient(left, 0, right, 0)
        if self.mode == "hue":
            stops = (
                (0.0, "#FF0000"), (1/6, "#FFFF00"), (2/6, "#00FF00"),
                (3/6, "#00FFFF"), (4/6, "#0000FF"), (5/6, "#FF00FF"), (1.0, "#FF0000")
            )
            for pos, color in stops:
                gradient.setColorAt(pos, QColor(color))
        else:
            gradient.setColorAt(0.0, self.palette().mid().color())
            gradient.setColorAt(1.0, self.palette().highlight().color())

        painter.setPen(QPen(self.palette().mid().color(), 1))
        painter.setBrush(gradient)
        painter.drawRoundedRect(left, groove_y, right-left, groove_h, 4, 4)

        length = self.style().pixelMetric(QStyle.PixelMetric.PM_SliderLength, option, self)
        available = max(1, self.width() - length)
        x = int((self.value() - self.minimum()) / max(1, self.maximum() - self.minimum()) * available + length / 2)
        painter.setBrush(self.palette().base())
        painter.setPen(QPen(self.palette().text().color(), 1))
        painter.drawEllipse(x - 7, self.height()//2 - 7, 14, 14)
        painter.end()
