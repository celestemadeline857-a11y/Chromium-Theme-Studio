from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Optional

from PySide6.QtCore import QTimer, Qt, QRect, QPoint
from PySide6.QtGui import (
    QPixmap,
    QPainter,
    QColor,
    QFont,
    QFontDatabase,
    QPainterPath,
    QPen,
)


@dataclass(frozen=True)
class BrowserMetrics:
    frame_h: int
    tabs_h: int
    toolbar_h: int
    bookmarks_h: int
    tab_w: int
    radius: int


class PreviewRenderer:
    """Deterministic browser mock renderer used by the v3 editor preview."""

    def __init__(self, home_page):
        self.w = home_page
        self._pixmap_cache: dict[str, QPixmap] = {}
        self._render_timer = QTimer()
        self._render_timer.setSingleShot(True)
        self._render_timer.timeout.connect(self._render_now)

    def c(self, key: str, default: str) -> QColor:
        value = self.w.theme_data.get(key, default)
        if not isinstance(value, str) or not value.startswith("#"):
            value = default
        if len(value) == 7:
            value += "FF"
        if len(value) != 9:
            value = default
        try:
            return QColor(
                int(value[1:3], 16),
                int(value[3:5], 16),
                int(value[5:7], 16),
                int(value[7:9], 16),
            )
        except ValueError:
            return QColor(default)

    def apply_theme(self) -> None:
        # Color changes are intentionally rendered immediately so the preview
        # follows sliders without a visible debounce/lag.
        self._render_now()

    def apply_image(self, mode: Optional[str] = None) -> None:
        self._render_now()

    def request_render(self) -> None:
        if not self._render_timer.isActive():
            self._render_timer.start(16)

    def invalidate_image_cache(self, path: Optional[str] = None) -> None:
        if path is None:
            self._pixmap_cache.clear()
        else:
            self._pixmap_cache.pop(path, None)

    def _load_pixmap(self, path: str) -> QPixmap:
        if path not in self._pixmap_cache:
            pix = QPixmap()
            if os.path.isfile(path):
                pix.load(path)
            self._pixmap_cache[path] = pix
        return self._pixmap_cache[path]

    @staticmethod
    def _metrics(browser: str) -> BrowserMetrics:
        if browser == "Edge":
            return BrowserMetrics(34, 40, 50, 28, 186, 7)
        if browser == "Brave":
            return BrowserMetrics(34, 42, 50, 28, 170, 8)
        return BrowserMetrics(34, 40, 50, 28, 158, 9)

    @staticmethod
    def _font(size: int, bold: bool = False) -> QFont:
        font = QFontDatabase.systemFont(QFontDatabase.GeneralFont)
        font.setPointSize(size)
        font.setBold(bold)
        return font

    @staticmethod
    def _fit_cover(pix: QPixmap, target: QRect) -> QPixmap:
        if pix.isNull() or target.width() <= 0 or target.height() <= 0:
            return QPixmap()
        return pix.scaled(
            max(1, target.width()),
            max(1, target.height()),
            Qt.KeepAspectRatioByExpanding,
            Qt.SmoothTransformation,
        )

    def _draw_cover(self, p: QPainter, pix: QPixmap, target: QRect, ox: int = 0, oy: int = 0) -> None:
        scaled = self._fit_cover(pix, target)
        if scaled.isNull():
            return
        src = QRect(
            max(0, (scaled.width() - target.width()) // 2 - ox),
            max(0, (scaled.height() - target.height()) // 2 - oy),
            min(target.width(), scaled.width()),
            min(target.height(), scaled.height()),
        )
        src = src.intersected(scaled.rect())
        if not src.isEmpty():
            p.drawPixmap(target, scaled, src)

    def _render_now(self) -> None:
        canvas_w = max(1, self.w.canvas.width())
        canvas_h = max(1, self.w.canvas.height())
        target = QPixmap(canvas_w, canvas_h)
        target.fill(self.c("preview_workspace", "#202124FF"))

        p = QPainter(target)
        p.setRenderHint(QPainter.Antialiasing, True)
        p.setRenderHint(QPainter.SmoothPixmapTransform, True)

        # The canvas is a workspace; the browser is an actual object inside it.
        margin_x = max(20, int(canvas_w * 0.025))
        margin_y = max(18, int(canvas_h * 0.035))
        browser_rect = QRect(
            margin_x,
            margin_y,
            max(200, canvas_w - margin_x * 2),
            max(180, canvas_h - margin_y * 2),
        )
        self._paint_browser(p, browser_rect)
        p.end()

        self.w.preview_surface.setPixmap(target)
        self.w.preview_surface.resize(canvas_w, canvas_h)
        self.w.preview_surface.show()
        if hasattr(self.w, "guides_layer"):
            self.w.guides_layer.resize(canvas_w, canvas_h)
            self.w.guides_layer.raise_()

    def _paint_browser(self, p: QPainter, rect: QRect) -> None:
        browser = self.w.browser_combo.currentText()
        m = self._metrics(browser)
        incognito = self.w.chk_incognito.isChecked()

        frame = self.c("frame_incognito" if incognito else "frame", "#3C4043FF")
        inactive = self.c(
            "inactive_tab_incognito" if incognito else "inactive_tab",
            "#E8EAEDFF",
        )
        active = self.c("active_tab", "#FFFFFFFF")
        tab_text = self.c("tab_text", "#202124FF")
        inactive_text = self.c("inactive_tab_text", "#5F6368FF")
        toolbar = self.c("toolbar", "#FFFFFFFF")
        toolbar_text = self.c("toolbar_text", "#5F6368FF")
        bookmark_text = self.c("bookmark_text", "#5F6368FF")
        button = self.c("button_tint", "#5F6368FF")
        omni_bg = self.c(
            "omnibox_background_incognito" if incognito else "omnibox_background",
            "#F1F3F4FF",
        )
        omni_text = self.c(
            "omnibox_text_incognito" if incognito else "omnibox_text",
            "#202124FF",
        )
        ntp_bg = self.c("ntp_background", "#FFFFFFFF")

        p.save()
        path = QPainterPath()
        path.addRoundedRect(rect, 12, 12)
        p.setClipPath(path)

        # Browser body first. This makes the theme's NTP colors immediately
        # visible instead of leaving the preview looking like an empty canvas.
        content_y = rect.y() + m.frame_h + m.tabs_h + m.toolbar_h + m.bookmarks_h
        content = QRect(
            rect.x(),
            content_y,
            rect.width(),
            max(1, rect.bottom() - content_y + 1),
        )
        p.fillRect(content, ntp_bg)

        ntp_path = self.w.theme_data.get("ntp_image")
        if ntp_path:
            pix = self._load_pixmap(ntp_path)
            if not pix.isNull():
                props = self.w.theme_data.get("ntp_image_properties", {}) or {}
                self._draw_cover(
                    p,
                    pix,
                    content,
                    int(props.get("x", 0)),
                    int(props.get("y", 0)),
                )

        # Browser frame strip.
        frame_rect = QRect(rect.x(), rect.y(), rect.width(), m.frame_h)
        p.fillRect(frame_rect, frame)
        frame_key = "frame_image_incognito" if incognito else "frame_image"
        frame_path = self.w.theme_data.get(frame_key)
        if frame_path:
            pix = self._load_pixmap(frame_path)
            if not pix.isNull():
                props = self.w.theme_data.get(f"{frame_key}_properties", {}) or {}
                self._draw_cover(
                    p,
                    pix,
                    frame_rect,
                    int(props.get("x", 0)),
                    int(props.get("y", 0)),
                )

        # Tab strip.
        tabs_rect = QRect(rect.x(), rect.y() + m.frame_h, rect.width(), m.tabs_h)
        p.fillRect(tabs_rect, frame)

        tab_y = tabs_rect.y() + 5
        tab_h = tabs_rect.height() - 5
        inactive_rect = QRect(rect.x() + 18, tab_y, m.tab_w, tab_h)
        active_rect = QRect(inactive_rect.right() + 8, tab_y, m.tab_w, tab_h)

        p.setPen(Qt.NoPen)
        p.setBrush(inactive)
        p.drawRoundedRect(inactive_rect, m.radius, m.radius)
        p.setBrush(active)
        p.drawRoundedRect(active_rect, m.radius, m.radius)

        p.setFont(self._font(9))
        p.setPen(inactive_text)
        p.drawText(
            inactive_rect.adjusted(13, 0, -8, 0),
            Qt.AlignVCenter | Qt.AlignLeft,
            "New Tab",
        )
        p.setFont(self._font(9, True))
        p.setPen(tab_text)
        p.drawText(
            active_rect.adjusted(13, 0, -8, 0),
            Qt.AlignVCenter | Qt.AlignLeft,
            "Theme Studio",
        )

        # Browser-specific tab affordance.
        plus_x = active_rect.right() + 12
        p.setPen(toolbar_text)
        pen = QPen(toolbar_text, 1.6, Qt.SolidLine, Qt.RoundCap)
        p.setPen(pen)
        p.drawLine(QPoint(plus_x, tab_y + tab_h // 2), QPoint(plus_x + 12, tab_y + tab_h // 2))
        p.drawLine(QPoint(plus_x + 6, tab_y + tab_h // 2 - 6), QPoint(plus_x + 6, tab_y + tab_h // 2 + 6))

        # Toolbar.
        toolbar_y = tabs_rect.bottom() + 1
        toolbar_rect = QRect(rect.x(), toolbar_y, rect.width(), m.toolbar_h)
        p.fillRect(toolbar_rect, toolbar)

        icon_y = toolbar_y + toolbar_rect.height() // 2
        p.setPen(QPen(button, 2, Qt.SolidLine, Qt.RoundCap))
        for x, direction in ((rect.x() + 24, -1), (rect.x() + 52, 1)):
            if direction < 0:
                p.drawLine(QPoint(x + 5, icon_y), QPoint(x - 4, icon_y))
                p.drawLine(QPoint(x - 4, icon_y), QPoint(x + 1, icon_y - 5))
                p.drawLine(QPoint(x - 4, icon_y), QPoint(x + 1, icon_y + 5))
            else:
                p.drawLine(QPoint(x - 5, icon_y), QPoint(x + 4, icon_y))
                p.drawLine(QPoint(x + 4, icon_y), QPoint(x - 1, icon_y - 5))
                p.drawLine(QPoint(x + 4, icon_y), QPoint(x - 1, icon_y + 5))

        url_rect = QRect(
            rect.x() + 76,
            toolbar_y + 8,
            max(150, rect.width() - 128),
            toolbar_rect.height() - 16,
        )
        p.setBrush(omni_bg)
        p.setPen(Qt.NoPen)
        p.drawRoundedRect(url_rect, url_rect.height() // 2, url_rect.height() // 2)
        p.setFont(self._font(9))
        p.setPen(omni_text)
        host = "chrome://newtab"
        if browser == "Brave":
            host = "brave://newtab"
        elif browser == "Edge":
            host = "edge://newtab"
        p.drawText(
            url_rect.adjusted(14, 0, -12, 0),
            Qt.AlignVCenter | Qt.AlignLeft,
            host,
        )

        # Menu dots are drawn geometrically so they render consistently across
        # Windows/Linux font configurations.
        dot_x = rect.right() - 22
        for dy in (-6, 0, 6):
            p.setBrush(button)
            p.drawEllipse(QPoint(dot_x, icon_y + dy), 1.8, 1.8)

        # Bookmarks row.
        bookmarks_y = toolbar_rect.bottom() + 1
        bookmarks_rect = QRect(rect.x(), bookmarks_y, rect.width(), m.bookmarks_h)
        p.fillRect(bookmarks_rect, toolbar)
        p.setFont(self._font(8))
        p.setPen(bookmark_text)
        x = rect.x() + 20
        for name in ("Gmail", "YouTube", "Maps", "Theme Store"):
            p.drawText(QRect(x, bookmarks_y, 86, m.bookmarks_h), Qt.AlignVCenter | Qt.AlignLeft, name)
            x += 86

        # Subtle browser body details make the preview read as a page rather
        # than a plain colored rectangle while keeping the actual NTP theme clear.
        if not ntp_path:
            heading = self.c("ntp_text", "#5F6368FF")
            p.setFont(self._font(18, True))
            p.setPen(heading)
            p.drawText(
                QRect(content.x() + 36, content.y() + 34, min(500, content.width() - 72), 36),
                Qt.AlignLeft | Qt.AlignVCenter,
                "New Tab",
            )
            p.setFont(self._font(10))
            p.setPen(self.c("inactive_tab_text", "#5F6368FF"))
            p.drawText(
                QRect(content.x() + 38, content.y() + 70, min(560, content.width() - 76), 28),
                Qt.AlignLeft | Qt.AlignVCenter,
                f"{browser} theme preview",
            )

        p.restore()

        # Outer border is kept outside the clip so the browser silhouette is
        # obvious against the workspace.
        p.setBrush(Qt.NoBrush)
        p.setPen(QPen(self.c("preview_border", "#5F6368AA"), 1))
        p.drawRoundedRect(rect, 12, 12)

    def get_processed_pixmap(self, mode: str) -> Optional[QPixmap]:
        path = self.w.theme_data.get(mode)
        if not path:
            return None
        pix = self._load_pixmap(path)
        if pix.isNull():
            return None
        props = self.w.theme_data.get(f"{mode}_properties", {}) or {}
        scale = max(0.01, float(props.get("scale", 100)) / 100.0)
        return pix.scaled(
            max(1, int(pix.width() * scale)),
            max(1, int(pix.height() * scale)),
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation,
        )
