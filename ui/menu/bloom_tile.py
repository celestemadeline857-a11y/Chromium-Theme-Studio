from PySide6.QtCore import Qt, Property, QPropertyAnimation, QEasingCurve
from PySide6.QtWidgets import QPushButton
from PySide6.QtGui import QPainter, QColor


class BloomTile(QPushButton):
    """Consistent editor navigation item with a small, fast hover response."""

    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setCheckable(True)
        self.setFixedHeight(36)
        self.setCursor(Qt.PointingHandCursor)
        self.setMouseTracking(True)
        self._indent = 14
        self._hover_progress = 0.0

        self.anim_indent = QPropertyAnimation(self, b"indent", self)
        self.anim_indent.setDuration(90)
        self.anim_indent.setEasingCurve(QEasingCurve.OutCubic)

        self.anim_hover = QPropertyAnimation(self, b"hover_progress", self)
        self.anim_hover.setDuration(90)
        self.anim_hover.setEasingCurve(QEasingCurve.OutCubic)
        self.toggled.connect(self.on_toggled)

    def on_toggled(self, checked):
        self.anim_indent.stop()
        self.anim_hover.stop()
        if checked:
            self.set_indent(14)
            self.set_hover_progress(0.0)
        else:
            self.set_indent(14)
            self.set_hover_progress(0.0)

    def get_indent(self):
        return self._indent

    def set_indent(self, value):
        self._indent = int(value)
        self.update()

    indent = Property(int, get_indent, set_indent)

    def get_hover_progress(self):
        return self._hover_progress

    def set_hover_progress(self, value):
        self._hover_progress = float(value)
        self.update()

    hover_progress = Property(float, get_hover_progress, set_hover_progress)

    def enterEvent(self, event):
        if not self.isChecked():
            self.anim_indent.stop()
            self.anim_indent.setStartValue(self._indent)
            self.anim_indent.setEndValue(18)
            self.anim_indent.start()
            self.anim_hover.stop()
            self.anim_hover.setStartValue(self._hover_progress)
            self.anim_hover.setEndValue(1.0)
            self.anim_hover.start()
        super().enterEvent(event)

    def leaveEvent(self, event):
        if not self.isChecked():
            self.anim_indent.stop()
            self.anim_indent.setStartValue(self._indent)
            self.anim_indent.setEndValue(14)
            self.anim_indent.start()
            self.anim_hover.stop()
            self.anim_hover.setStartValue(self._hover_progress)
            self.anim_hover.setEndValue(0.0)
            self.anim_hover.start()
        super().leaveEvent(event)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing, True)

        dark = self.palette().window().color().value() < 160
        text_color = self.palette().text().color()

        if self.isChecked():
            bg = QColor("#303238") if dark else QColor("#E8F0FE")
            accent = QColor("#8AB4F8") if dark else QColor("#1A73E8")
            final_text = self.palette().windowText().color()
            font = self.font()
            font.setBold(True)

            p.setPen(Qt.NoPen)
            p.setBrush(bg)
            p.drawRoundedRect(self.rect(), 7, 7)
            p.setBrush(accent)
            p.drawRoundedRect(0, 8, 3, self.height() - 16, 1.5, 1.5)
        else:
            if self._hover_progress > 0.01:
                hover = QColor("#2A2C31") if dark else QColor("#F1F3F4")
                p.setPen(Qt.NoPen)
                p.setBrush(hover)
                p.setOpacity(self._hover_progress)
                p.drawRoundedRect(self.rect(), 7, 7)
                p.setOpacity(1.0)
            final_text = text_color
            font = self.font()
            font.setBold(False)

        p.setFont(font)
        p.setPen(final_text)
        text_rect = self.rect().adjusted(self._indent, 0, -10, 0)
        p.drawText(text_rect, Qt.AlignVCenter | Qt.AlignLeft, self.text())
        p.end()
