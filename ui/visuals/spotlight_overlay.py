import math

from PySide6.QtCore import QPoint, QPointF, QRectF, Qt, QTimer
from PySide6.QtGui import QColor, QCursor, QPainter, QPainterPath, QRadialGradient, QBrush
from PySide6.QtWidgets import QAbstractButton, QApplication, QWidget

from ui.menu.bloom_tile import BloomTile


class SpotlightOverlay(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.setAttribute(Qt.WA_NoSystemBackground)
        self.setAttribute(Qt.WA_TranslucentBackground)

        self.palette_light = {"base": QColor("#FBC02D"), "active": QColor("#F50057")}
        self.palette_dark = {"base": QColor("#FFD700"), "active": QColor("#00FFFF")}
        self.base_color = self.palette_light["base"]
        self.active_color = self.palette_light["active"]
        self.base_radius = 80.0
        self.magnetic_strength = 0.15
        self.opacity_factor = 0.85
        self.cursor_pos = QPointF()
        self.light_pos = QPointF()
        self.current_color = QColor(self.base_color)
        self.current_radius = self.base_radius
        self.target_path = None
        self.is_visible = True
        self.is_dark_mode = False
        self.was_locked = False

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_physics)
        self.timer.start(16)

    def update_settings(self, radius, strength, opacity, c_lb, c_la, c_db, c_da):
        self.base_radius = max(1.0, float(radius))
        self.magnetic_strength = max(0.0, min(1.0, float(strength)))
        self.opacity_factor = max(0.0, min(1.0, float(opacity)))
        self.palette_light["base"] = QColor(c_lb)
        self.palette_light["active"] = QColor(c_la)
        self.palette_dark["base"] = QColor(c_db)
        self.palette_dark["active"] = QColor(c_da)
        self.set_theme_mode(self.is_dark_mode)
        self.update()

    def set_theme_mode(self, is_dark):
        self.is_dark_mode = bool(is_dark)
        palette = self.palette_dark if self.is_dark_mode else self.palette_light
        self.base_color = palette["base"]
        self.active_color = palette["active"]

    def set_active_state(self, enabled):
        self.is_visible = bool(enabled)
        self.setVisible(self.is_visible)
        if self.is_visible:
            self.timer.start(16)
        else:
            self.timer.stop()

    def update_physics(self):
        if not self.is_visible or not self.isVisible():
            return
        local = self.mapFromGlobal(QCursor.pos())
        self.cursor_pos = QPointF(local)

        hovered = self.parentWidget().childAt(local) if self.parentWidget() else None
        final_target = None
        cursor = hovered
        while cursor and cursor is not self.parentWidget():
            if isinstance(cursor, BloomTile):
                final_target = cursor
                break
            if isinstance(cursor, QAbstractButton):
                final_target = cursor
                break
            cursor = cursor.parentWidget()

        apply_magnet = False
        if final_target:
            if isinstance(final_target, BloomTile):
                apply_magnet = True
            else:
                excluded = {"TopBar", "SettingsPage", "ExportPage"}
                parent = final_target
                while parent and parent is not self.parentWidget():
                    if parent.__class__.__name__ in excluded:
                        break
                    parent = parent.parentWidget()
                else:
                    apply_magnet = True

        if self.was_locked and not apply_magnet:
            self.current_radius = 0.0
        self.was_locked = apply_magnet

        target_color = self.base_color
        target_pos = self.cursor_pos
        target_radius = self.base_radius
        self.target_path = None

        if apply_magnet:
            target_color = self.active_color
            top_left = self.mapFromGlobal(final_target.mapToGlobal(QPoint(0, 0)))
            rect = QRectF(QPointF(top_left), QPointF(top_left) + QPointF(final_target.size()))
            center = rect.center()
            path = QPainterPath()
            path.addRoundedRect(rect, 8, 8)
            self.target_path = path
            diff = self.cursor_pos - center
            factor = max(0.1, 0.5 - self.magnetic_strength * 2.0)
            target_pos = center + diff * factor
            target_radius = max(rect.width(), rect.height()) * 0.9

        self.light_pos = self.light_pos * 0.8 + target_pos * 0.2
        self.current_radius = self.current_radius * 0.85 + target_radius * 0.15
        r = int(self.current_color.red() * 0.92 + target_color.red() * 0.08)
        g = int(self.current_color.green() * 0.92 + target_color.green() * 0.08)
        b = int(self.current_color.blue() * 0.92 + target_color.blue() * 0.08)
        self.current_color = QColor(r, g, b)
        self.update()

    def paintEvent(self, event):
        if not self.is_visible:
            return
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.setCompositionMode(QPainter.CompositionMode_SourceOver)
        if self.target_path:
            painter.setClipPath(self.target_path)
        gradient = QRadialGradient(self.light_pos, max(1.0, self.current_radius))
        c = self.current_color
        alpha = int(255 * self.opacity_factor)
        gradient.setColorAt(0.0, QColor(c.red(), c.green(), c.blue(), alpha))
        gradient.setColorAt(1.0, QColor(c.red(), c.green(), c.blue(), 0))
        painter.setBrush(QBrush(gradient))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(self.light_pos, self.current_radius, self.current_radius)
        painter.end()
