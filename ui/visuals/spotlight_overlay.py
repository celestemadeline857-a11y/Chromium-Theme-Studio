from PySide6.QtCore import QPoint, QPointF, QRectF, Qt, QTimer
from PySide6.QtGui import QColor, QCursor, QPainter, QPainterPath, QRadialGradient, QBrush
from PySide6.QtWidgets import QAbstractButton, QWidget

from ui.menu.bloom_tile import BloomTile


class SpotlightOverlay(QWidget):
    """Lightweight 60 FPS spotlight with stable magnetic easing.

    The spotlight never snaps its radius to zero or freezes on a button. Target
    position, radius, and colour are all eased independently, so entering and
    leaving a control feels continuous.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.setAttribute(Qt.WA_NoSystemBackground)
        self.setAttribute(Qt.WA_TranslucentBackground)

        self.palette_light = {"base": QColor("#FBC02D"), "active": QColor("#F50057")}
        self.palette_dark = {"base": QColor("#FFD700"), "active": QColor("#00FFFF")}
        self.base_color = QColor(self.palette_light["base"])
        self.active_color = QColor(self.palette_light["active"])

        self.base_radius = 80.0
        self.magnetic_strength = 0.15
        self.opacity_factor = 0.85

        self.cursor_pos = QPointF()
        self.light_pos = QPointF()
        self.current_color = QColor(self.base_color)
        self.current_radius = self.base_radius
        self.target_radius = self.base_radius
        self.target_path = None
        self.target_pos = QPointF()
        self.is_visible = True
        self.is_dark_mode = False
        self._last_target = None

        self.timer = QTimer(self)
        self.timer.setInterval(16)
        self.timer.timeout.connect(self.update_physics)
        self.timer.start()

    def update_settings(self, radius, strength, opacity, c_lb, c_la, c_db, c_da):
        self.base_radius = max(8.0, float(radius))
        self.magnetic_strength = max(0.0, min(1.0, float(strength)))
        self.opacity_factor = max(0.0, min(1.0, float(opacity)))
        self.palette_light["base"] = QColor(c_lb)
        self.palette_light["active"] = QColor(c_la)
        self.palette_dark["base"] = QColor(c_db)
        self.palette_dark["active"] = QColor(c_da)
        self.set_theme_mode(self.is_dark_mode)
        if not self._last_target:
            self.current_radius = self.base_radius
            self.target_radius = self.base_radius
        self.update()

    def set_theme_mode(self, is_dark):
        self.is_dark_mode = bool(is_dark)
        palette = self.palette_dark if self.is_dark_mode else self.palette_light
        self.base_color = QColor(palette["base"])
        self.active_color = QColor(palette["active"])

    def set_active_state(self, enabled):
        self.is_visible = bool(enabled)
        self.setVisible(self.is_visible)
        if self.is_visible:
            self.timer.start()
        else:
            self.timer.stop()

    def _find_target(self, local):
        hovered = self.parentWidget().childAt(local) if self.parentWidget() else None
        target = hovered
        while target and target is not self.parentWidget():
            if isinstance(target, BloomTile):
                return target
            if isinstance(target, QAbstractButton):
                excluded = {"TopBar", "SettingsPage", "ExportPage"}
                parent = target
                while parent and parent is not self.parentWidget():
                    if parent.__class__.__name__ in excluded:
                        return None
                    parent = parent.parentWidget()
                return target
            target = target.parentWidget()
        return None

    @staticmethod
    def _approach(current, target, response=0.20):
        return current + (target - current) * response

    def update_physics(self):
        if not self.is_visible or not self.isVisible():
            return

        self.cursor_pos = QPointF(self.mapFromGlobal(QCursor.pos()))
        target = self._find_target(self.cursor_pos)

        self.target_path = None
        self.target_pos = QPointF(self.cursor_pos)
        self.target_radius = self.base_radius

        if target is not None:
            top_left = QPointF(self.mapFromGlobal(target.mapToGlobal(QPoint(0, 0))))
            rect = QRectF(top_left, top_left + QPointF(target.size()))
            center = rect.center()

            path = QPainterPath()
            path.addRoundedRect(rect, min(9.0, rect.height() / 3.0), min(9.0, rect.height() / 3.0))
            self.target_path = path

            # Magnetic pull controls how strongly the light is attracted to the
            # control centre.  It never overshoots and never stalls.
            attraction = 0.35 + self.magnetic_strength * 0.55
            self.target_pos = center + (self.cursor_pos - center) * (1.0 - attraction)
            self.target_radius = max(rect.width(), rect.height()) * 0.72

        self._last_target = target
        self.light_pos = self._approach(self.light_pos, self.target_pos, 0.22)
        self.current_radius += (self.target_radius - self.current_radius) * 0.18

        tr, tg, tb = self.base_color.red(), self.base_color.green(), self.base_color.blue()
        if target is not None:
            tr, tg, tb = self.active_color.red(), self.active_color.green(), self.active_color.blue()

        self.current_color = QColor(
            int(self.current_color.red() + (tr - self.current_color.red()) * 0.14),
            int(self.current_color.green() + (tg - self.current_color.green()) * 0.14),
            int(self.current_color.blue() + (tb - self.current_color.blue()) * 0.14),
        )
        self.update()

    def paintEvent(self, event):
        if not self.is_visible:
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)

        # Clip only while magnetically attached. When the cursor leaves, the
        # clip disappears immediately while the light itself eases back out.
        if self._last_target is not None and self.target_path is not None:
            painter.save()
            painter.setClipPath(self.target_path)

        radius = max(1.0, self.current_radius)
        c = self.current_color
        alpha = int(255 * self.opacity_factor)
        gradient = QRadialGradient(self.light_pos, radius)
        gradient.setColorAt(0.0, QColor(c.red(), c.green(), c.blue(), alpha))
        gradient.setColorAt(0.55, QColor(c.red(), c.green(), c.blue(), int(alpha * 0.32)))
        gradient.setColorAt(1.0, QColor(c.red(), c.green(), c.blue(), 0))

        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(gradient))
        painter.drawEllipse(self.light_pos, radius, radius)

        if self._last_target is not None and self.target_path is not None:
            painter.restore()

        painter.end()
