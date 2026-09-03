from PySide6.QtCore import Qt
from PySide6.QtGui import QMouseEvent, QWheelEvent
from PySide6.QtWidgets import QSlider, QStyle


class SmartSlider(QSlider):
    """Consistent, mouse-friendly slider used throughout the editor."""

    def __init__(self, orientation, parent=None):
        super().__init__(orientation, parent)
        self.setMouseTracking(True)
        self.setFocusPolicy(Qt.StrongFocus)
        self.setTracking(True)
        self.setSingleStep(1)
        self.setPageStep(max(1, (self.maximum() - self.minimum()) // 10 or 1))
        self.next_slider = None
        self.prev_slider = None

    def _set_from_position(self, x):
        groove = max(1, self.width() - self.style().pixelMetric(
            QStyle.PixelMetric.PM_SliderLength, None, self
        ))
        length = self.style().pixelMetric(
            self.style().PixelMetric.PM_SliderLength, None, self
        )
        pos = max(0, min(groove, int(x - length / 2)))
        value = self.minimum() + round(
            pos * (self.maximum() - self.minimum()) / groove
        )
        self.setValue(value)

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton and self.orientation() == Qt.Horizontal:
            self._set_from_position(event.position().x())
            event.accept()
            return
        super().mousePressEvent(event)

    def wheelEvent(self, event: QWheelEvent):
        delta = event.angleDelta().y()
        if delta:
            step = self.singleStep() * (10 if event.modifiers() & Qt.ControlModifier else 1)
            self.setValue(self.value() + (step if delta > 0 else -step))
            event.accept()
            return
        super().wheelEvent(event)

    def enterEvent(self, event):
        self.setFocus(Qt.MouseFocusReason)
        super().enterEvent(event)

    def keyPressEvent(self, event):
        step = 10 if (event.modifiers() & Qt.ControlModifier) else 1
        if event.key() in (Qt.Key_Up, Qt.Key_Right):
            self.setValue(self.value() + step)
            event.accept()
        elif event.key() in (Qt.Key_Down, Qt.Key_Left):
            self.setValue(self.value() - step)
            event.accept()
        else:
            super().keyPressEvent(event)
